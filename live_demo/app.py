"""Muse Guard live check, served from one Modal app.

Only POST /api/extract calls a model. /api/check and /api/approve are deterministic.
Visitor text is never logged or stored; logs carry counts, cost and error names only.
"""
import asyncio
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.request
from pathlib import Path

import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from muse_guard.gateway import MODEL, NoRedirect, response_usage
from spec_guard.core import digest, domain_errors, matches, review, space, validate
from spec_guard.provider import PROMPT
from submission_tools.decision_preview import preview, summary

HERE = Path(__file__).resolve().parent
MAX_DOC_CHARS = 2000
MAX_OUTPUT_TOKENS = 2048
TIMEOUT_SECONDS = 30
RESERVATION_USD = 0.03
BUDGET_TOTAL_USD = 10.0
VISITOR_LIMIT_PER_HOUR = 5
MAX_BODY_BYTES = 64 * 1024
NOT_CHECKED = [
    'Only the input values you declare are checked. Values outside the declared fields are not.',
    'It does not confirm that the model read your text correctly. Check each rule against its source sentence.',
    'It does not write, run or test code. Code changes are shown only as a recorded run.',
    'It does not judge business, legal or safety impact, or which rule should win. You choose that.',
    'A result means "checked over declared inputs". It is not a proof.',
]

app = modal.App('muse-guard-live')
image = modal.Image.debian_slim(python_version='3.13').pip_install('fastapi==0.115.8')
if modal.is_local():
    REPO = HERE.parent
    image = (image
             .add_local_dir(REPO / 'muse_guard', '/root/muse_guard', ignore=['**/__pycache__/**'])
             .add_local_dir(REPO / 'spec_guard', '/root/spec_guard', ignore=['**/__pycache__/**'])
             .add_local_file(REPO / 'submission_tools' / 'decision_preview.py', '/root/submission_tools/decision_preview.py')
             .add_local_dir(HERE / 'static', '/root/static', ignore=['**/__pycache__/**'])
             .add_local_file(HERE / 'samples.json', '/root/samples.json'))


class Ledger:
    """Public-demo spend and per-visitor limits, kept in a dict-like store (modal.Dict in production)."""

    def __init__(self, store):
        self.store = store
        self.lock = threading.Lock()

    def budget(self):
        return self.store.get('budget', {'spent_usd': 0.0, 'pending_usd': 0.0, 'unknown': False})

    def live_open(self):
        b = self.budget()
        return not b['unknown'] and b['spent_usd'] + b['pending_usd'] + RESERVATION_USD <= BUDGET_TOTAL_USD

    def reserve(self):
        with self.lock:
            if not self.live_open():
                return False
            b = self.budget()
            b['pending_usd'] = round(b['pending_usd'] + RESERVATION_USD, 6)
            self.store['budget'] = b
            return True

    def settle(self, cost):
        with self.lock:
            b = self.budget()
            b['pending_usd'] = round(max(0.0, b['pending_usd'] - RESERVATION_USD), 6)
            # Unknown usage, or usage above the reservation, stops live extraction until someone checks it.
            if cost is None or cost > RESERVATION_USD:
                b['unknown'] = True
            else:
                b['spent_usd'] = round(b['spent_usd'] + cost, 6)
            self.store['budget'] = b

    def admit(self, visitor):
        key = 'visitor:%s:%d' % (visitor, int(time.time() // 3600))
        with self.lock:
            count = self.store.get(key, 0)
            if count >= VISITOR_LIMIT_PER_HOUR:
                return False
            self.store[key] = count + 1
            return True


def cost_usd(usage):
    if usage is None:
        return None
    fresh = usage['input_tokens'] - usage['cached_input_tokens']
    total = fresh * 1.25 + usage['cached_input_tokens'] * 0.15 + usage['output_tokens'] * 4.25
    return round(total / 1000000, 8)


def meta_post(payload):
    """Single POST to Meta's Responses endpoint. The key is read here and never returned or logged."""
    key = os.environ.get('META_API_KEY')
    if not key:
        raise RuntimeError('no key configured')
    request = urllib.request.Request('https://api.meta.ai/v1/responses', data=json.dumps(payload).encode(),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=TIMEOUT_SECONDS) as reply:
        return reply.read(4 * 1024 * 1024)


def read_proposal(raw):
    """Same parsing as spec_guard.provider.propose(): join output_text, then parse JSON."""
    usage = response_usage(raw)
    try:
        response = json.loads(raw)
    except ValueError:
        return {'invalid_response': 'Spark returned an unreadable response'}, usage
    if not isinstance(response, dict) or response.get('status') != 'completed':
        return {'invalid_response': 'Spark did not complete the extraction'}, usage
    text = ''.join(part.get('text', '') for item in response.get('output', []) if isinstance(item, dict)
                   and item.get('type') == 'message' for part in item.get('content', [])
                   if isinstance(part, dict) and part.get('type') == 'output_text')
    try:
        return json.loads(text), usage
    except ValueError:
        return {'invalid_response': text or 'No proposed rules returned'}, usage


def extraction_view(doc, proposal):
    checked = validate(doc, proposal)
    rules = [item for item in checked['items'] if item['valid'] and item['kind'] == 'rule']
    items = []
    for item in checked['items']:
        row = {'key': item['key'], 'kind': item['kind'], 'valid': item['valid'], 'errors': item['errors'],
               'proposal': item['proposal']}
        if item['valid'] and item['kind'] == 'rule':
            hits = [value for value in space(checked['input_space']) if matches(item['proposal'], value)]
            alone = [value for value in hits
                     if not any(matches(other['proposal'], value) for other in rules if other is not item)]
            row['example'] = next(iter(alone or hits), None)
            row['example_alone'] = bool(alone)
        items.append(row)
    return {'input_space': checked['input_space'], 'items': items, 'errors': checked['errors'],
            'unconverted': checked['unconverted']}


def run_review(doc, proposal, decisions, response_kind='unverified'):
    record = review(doc, proposal, lambda item: decisions.get(item['key']) is True, response_kind=response_kind)
    table = record['confirmed']
    groups = []
    if table['rules'] and not domain_errors(table['input_space']):
        groups = preview(table)['groups']
    return record, groups


def check_payload(record, groups):
    table = record['confirmed']
    checked = 0 if domain_errors(table['input_space']) else len(space(table['input_space']))
    return {'confirmed_rules': table['rules'], 'checked_inputs': checked,
            'clashes': [{'rules': g['rules'], 'summary': summary(g), 'affected_inputs': g['affected_inputs'],
                         'choices': g['choices'], 'rows': g['rows']} for g in groups],
            'uncovered_count': len(record['uncovered_inputs']), 'uncovered_examples': record['uncovered_inputs'][:5],
            'unconverted': record['validation']['unconverted'], 'errors': record['validation']['errors'],
            'confirmed_sha256': record['confirmed_sha256']}


def topo_order(ids, edges):
    """Total order where each winner precedes its loser. Original rule order breaks ties."""
    order, remaining = [], list(ids)
    while remaining:
        ready = [r for r in remaining if not any(loser == r and winner in remaining for winner, loser in edges)]
        if not ready:
            raise ValueError('The chosen winners contradict each other. Choose a consistent order.')
        order.append(ready[0])
        remaining.remove(ready[0])
    return order


def outcome(table, value):
    for rule_id in table['priority']:
        rule = next(r for r in table['rules'] if r['id'] == rule_id)
        if matches(rule, value):
            return rule['action']
    return table['default']


def approve_choices(doc, proposal, decisions, winners, origin, mode, kind):
    record, groups = run_review(doc, proposal, decisions, kind)
    if record['validation']['errors']:
        raise ValueError('The rule table has errors. Fix the rules first.')
    if record['uncovered_inputs']:
        raise ValueError('Some declared inputs have no rule and no fallback. Confirm a fallback or change the text.')
    table = record['confirmed']
    if not table['rules']:
        raise ValueError('Confirm at least one rule.')
    keys = {'+'.join(g['rules']) for g in groups}
    if set(winners) - keys:
        raise ValueError('Unknown conflict in winner choices.')
    edges, chosen = [], []
    for group in groups:
        key = '+'.join(group['rules'])
        winner = winners.get(key)
        if winner not in group['rules']:
            raise ValueError('Choose a winner for ' + ' vs '.join(group['rules']) + '.')
        loser = group['rules'][1] if winner == group['rules'][0] else group['rules'][0]
        edges.append((winner, loser))
        chosen.append({'rules': group['rules'], 'winner': winner, 'affected_inputs': group['affected_inputs']})
    priority = topo_order([r['id'] for r in table['rules']], edges)
    v2 = dict(table, version=2, priority=priority, parent_hash=digest(table), decisions=chosen)
    checks = []
    for group in groups:
        winner = winners['+'.join(group['rules'])]
        index = group['rules'].index(winner)
        for row in group['rows']:
            if outcome(v2, row['input']) != row['actions'][index]:
                raise RuntimeError('Approved order does not match the decision preview.')
        checks.append({'rules': group['rules'], 'winner': winner, 'inputs_checked': len(group['rows']),
                       'all_match': True})
    evidence = {'schema': 1, 'kind': 'muse-guard live check evidence', 'mode': mode,
                'model_responses': 'recorded %s extraction' % kind if kind in ('real', 'fake') else 'page-submitted; not checked by the server',
                'extraction_origin': origin, 'model': MODEL, 'doc_sha256': record['doc_sha256'],
                'proposal_sha256': record['proposal_sha256'], 'confirmed_sha256': record['confirmed_sha256'],
                'approved_rules_sha256': digest(v2), 'decisions': record['decisions'], 'choices': chosen,
                'checks': checks, 'checked_inputs': len(space(table['input_space'])),
                'statement': 'Checked over declared inputs only. Not a proof. No code was run.',
                'not_checked': NOT_CHECKED}
    return {'approved_rules': v2, 'evidence': evidence}


def visitor_key(request):
    forwarded = request.headers.get('x-forwarded-for', '').split(',')[0].strip()
    ip = forwarded or (request.client.host if request.client else 'unknown')
    salt = os.environ.get('RATE_SALT', 'muse-guard-live').encode()
    return hmac.new(salt, ip.encode(), hashlib.sha256).hexdigest()[:24]


def error(status, code, message):
    return JSONResponse({'error': code, 'message': message}, status_code=status)


async def read_json(request):
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        return None
    try:
        body = json.loads(raw)
    except ValueError:
        return None
    return body if isinstance(body, dict) else None


def load_samples(path):
    samples = json.loads(Path(path).read_text())
    for sample in samples:
        sample['view'] = extraction_view(sample['doc'], sample['proposal'])
    return samples


def create_app(model_call, store, mode, samples_path=HERE / 'samples.json'):
    """model_call(payload) -> raw Responses bytes, or None when live extraction is off."""
    ledger = Ledger(store)
    samples = load_samples(samples_path)
    api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    api.mount('/recorded', StaticFiles(directory=HERE / 'static' / 'recorded'), name='recorded')

    @api.get('/', response_class=HTMLResponse)
    def index():
        return HTMLResponse((HERE / 'static' / 'index.html').read_text(), headers={
            'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                                       "connect-src 'self'; base-uri 'none'; form-action 'none'",
            'X-Content-Type-Options': 'nosniff'})

    @api.get('/samples')
    def get_samples():
        return {'mode': mode, 'live_extraction': model_call is not None and ledger.live_open(),
                'max_chars': MAX_DOC_CHARS, 'samples': samples}

    @api.post('/api/extract')
    async def extract(request: Request):
        body = await read_json(request)
        doc = body.get('doc') if body else None
        if not isinstance(doc, str) or not doc.strip():
            return error(422, 'empty', 'Paste requirements text first.')
        if len(doc) > MAX_DOC_CHARS:
            return error(413, 'too_long', 'Requirements must be 2,000 characters or fewer.')
        if model_call is None:
            return error(503, 'live_unavailable', 'Live extraction is not configured here. Use a sample or the recorded run.')
        if not ledger.live_open():
            return error(503, 'live_paused', 'Live extraction is paused: the public budget is spent or a usage result was unknown. Use a sample or the recorded run.')
        if not ledger.admit(visitor_key(request)):
            return error(429, 'rate_limited', 'Five live extractions per hour per visitor. Try again later.')
        if not ledger.reserve():
            return error(503, 'budget_exhausted', 'The public demo budget is spent. Use a sample or the recorded run.')
        payload = {'model': MODEL, 'instructions': PROMPT, 'input': doc, 'max_output_tokens': MAX_OUTPUT_TOKENS,
                   'store': False, 'reasoning': {'effort': 'minimal'}}
        try:
            raw = await asyncio.to_thread(model_call, payload)
            proposal, usage = read_proposal(raw)
        except Exception as exc:  # no retries; provider text is never shown
            ledger.settle(None)
            print(json.dumps({'event': 'extract', 'outcome': 'model_error', 'error': type(exc).__name__}))
            return error(502, 'model_error', 'The live extraction failed. Use a sample or the recorded run.')
        cost = cost_usd(usage)
        ledger.settle(cost)
        print(json.dumps({'event': 'extract', 'outcome': 'ok', 'input_chars': len(doc), 'cost_usd': cost}))
        return {'proposal': proposal, 'view': extraction_view(doc, proposal), 'origin': 'live request', 'model': MODEL}

    @api.post('/api/check')
    async def check(request: Request):
        body = await read_json(request)
        doc, proposal, decisions = (body or {}).get('doc'), (body or {}).get('proposal'), (body or {}).get('decisions')
        if not isinstance(doc, str) or len(doc) > MAX_DOC_CHARS or not isinstance(proposal, dict) \
                or not isinstance(decisions, dict):
            return error(422, 'bad_request', 'Send doc, proposal and decisions.')
        record, groups = run_review(doc, proposal, decisions)
        return check_payload(record, groups)

    @api.post('/api/approve')
    async def approve(request: Request):
        body = await read_json(request)
        doc, proposal, decisions = (body or {}).get('doc'), (body or {}).get('proposal'), (body or {}).get('decisions')
        winners = (body or {}).get('winners')
        if not isinstance(doc, str) or len(doc) > MAX_DOC_CHARS or not isinstance(proposal, dict) \
                or not isinstance(decisions, dict) or not isinstance(winners, dict):
            return error(422, 'bad_request', 'Send doc, proposal, decisions and winners.')
        origin, kind = 'page-submitted proposal (model output not checked by the server)', 'unverified'
        for sample in samples:
            if sample['doc'] == doc and digest(sample['proposal']) == digest(proposal):
                origin, kind = 'recorded extraction: ' + sample['id'], sample['response_kind']
        try:
            return approve_choices(doc, proposal, decisions, winners, origin, mode, kind)
        except ValueError as exc:
            return error(422, 'cannot_approve', str(exc))

    return api


@app.function(image=image, secrets=[modal.Secret.from_name('muse-guard-meta')], max_containers=1, timeout=120)
@modal.concurrent(max_inputs=4)
@modal.asgi_app()
def web():
    has_key = bool(os.environ.get('META_API_KEY'))
    store = modal.Dict.from_name('muse-guard-live-state', create_if_missing=True)
    return create_app(meta_post if has_key else None, store, mode='live')
