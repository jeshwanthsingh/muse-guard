"""Baseline HTTP -> reviewed rules -> decision -> service edit -> isolated HTTP recheck."""
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid
from spec_guard.core import review,domain_errors
from spec_guard.cli import decision as review_translation
from muse_guard.rules import actions,digest,approved,approve
from submission_tools.continuous import reviewed_requirements,approve_decision
from submission_tools.decision_preview import preview,cli_preview
from returns_demo import provider
from returns_demo.source import ROOT,BASELINE_COMMIT,baseline_files
from returns_demo.preflight import prove
from returns_demo.checker import check
from returns_demo.agent import edit

FAKE='constructed fake Spark and Muse service responses; not observed model behavior'
SCOPE='Policy behavior checked over these declared cases.'


def approved_visible_tests(req):
    if req.get('version')!=2 or not approved(req):raise ValueError('Only approved v2 may update visible policy tests')
    # Only the three existing visible policy tests; the fourth HTTP case stays
    # checker-only. Approval, not an agent edit, replaces obsolete expectations.
    cases=[('eligible_fraud_held',True,True),('eligible_not_held',True,False),('ineligible_not_held',False,False)]
    lines=['import unittest','from refund_policy import next_action','class ApprovedPolicy(unittest.TestCase):']
    for name,eligible,held in cases:
        value={'eligible':eligible,'fraud_hold':held};expected=actions(req,value)
        if len(expected)!=1:raise ValueError('Approved rules still conflict')
        lines.append(' def test_'+name+'(self):self.assertEqual(next_action('+repr(value)+'), '+repr(expected[0])+')')
    return ('\n'.join(lines)+'\n').encode()


def hash_files(files):return {name:hashlib.sha256(data).hexdigest() for name,data in files.items()}


def validate_service_table(req):
    domains=req.get('input_space',{})
    if domain_errors(domains) or set(domains)!={'eligible','fraud_hold'}:raise ValueError('Service requires only the two declared Boolean policy fields')
    if any(set(map(type,v))!={bool} or set(v)!={True,False} for v in domains.values()):raise ValueError('Service fields require true/false domains; no silent conversion')
    if {r['id'] for r in req['rules']}!={'A','B'} or len(req['rules'])!=2:raise ValueError('Review exactly rules A and B for this service demo')
    if req['default']!='reject' or {r['action'] for r in req['rules']}!={'refund_immediately','manual_review'}:
        raise ValueError('Reviewed actions must match the service contract: refund_immediately, manual_review, reject; no silent aliases')


def run(out,*,fake_packet=None,reviewer=None,input_fn=None):
    if fake_packet is None:provider.require_real_date()
    elif fake_packet.get('kind')!=FAKE:raise ValueError('Fake responses must be explicitly labeled')
    out=Path(out)
    if out.exists():raise ValueError('Choose a new run folder; no overwrite or automatic retry')
    out.mkdir(parents=True)
    started=time.monotonic();identity='returns-service-'+uuid.uuid4().hex[:12]
    record={'schema':1,'run_id':identity,'kind':'returns-service recovery demo','response_kind':'fake' if fake_packet else 'real',
            'fake_notice':FAKE if fake_packet else None,'status':'BASELINE','scope':SCOPE,'baseline_commit':BASELINE_COMMIT,
            'started_at':datetime.now(timezone.utc).isoformat(),'runtime_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
            'runtime_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
            'cost_usd':0 if fake_packet else None,'paid_calls':0,'study':False}
    token=provider.RUN_ID.set(identity)
    def save():
        from returns_demo.view import render
        (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
        (out/'index.html').write_text(render(record))
    def receipts():
        if fake_packet is not None:return []
        return [r for p in provider.RESULTS.glob('returns-*.json') if (r:=json.loads(p.read_text())).get('service_run_id')==identity]
    try:
        # All isolation and baseline work precedes the first possible paid call.
        record['isolation']=prove();files=baseline_files()
        record['baseline_source_sha256']=hash_files(files)
        record['baseline']=check(files)
        if record['baseline']['outcome']!='PASS':raise ValueError('Baseline HTTP checks failed; no extraction call made')
        artifacts=out/'artifacts';artifacts.mkdir()
        for name,data in files.items():
            target=artifacts/'v1'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(data)
        record['status']='REVIEWING RULES';save()
        doc=(ROOT/'demo/returns-service/refund.md').read_text()
        record['doc_sha256']=hashlib.sha256(doc.encode()).hexdigest()
        if fake_packet is None:proposal,cost=provider.propose(doc)
        else:proposal=fake_packet['proposal'];cost={'cost_usd':0,'model_invoked':False,'kind':'constructed fake Spark response'}
        accepted=[]
        def choose(item):
            if reviewer is not None:return reviewer(item)
            if fake_packet is not None:
                answer=fake_packet['review'][len(accepted)];accepted.append(answer);return answer
            return review_translation(item)
        spec=review(doc,proposal,choose,response_kind=record['response_kind'],cost=cost)
        record.update(spec=spec,extraction_cost=cost)
        if any(d['decision']!='confirmed' for d in spec['decisions']) or len(spec['decisions'])!=3:
            record['status']='REVIEW REJECTED';return record
        req=reviewed_requirements(spec);validate_service_table(req)
        record['requirements_v1']=req;record['decision_preview']=preview(req)
        if record['decision_preview']['conflicts']!=1:raise ValueError('Expected one verified A/B conflict; review extraction, no automatic retry')
        record['status']='AWAITING DECISION';save();print(cli_preview(req),flush=True)
        if fake_packet is not None:
            answer=fake_packet['decision']
            record['decision_provenance']='constructed fake fixture choice; not a human decision'
        else:
            answer=(input_fn or input)('Your choice — A or B (no delegated choice): ').strip().upper()
            if answer not in ('A','B'):raise ValueError('Explicit human A/B choice required; no choice was delegated')
            record['decision_provenance']='interactive human CLI choice'
        if fake_packet is not None:
            clash=spec['clashes'][0]
            report={'conflict':True,'rules':clash['rules'],'witness':clash['witness'],'explanation':'Verified fake-fixture decision'}
            approved=approve(req,answer,report,confirmed=True,source='simulated developer CLI')
        else:approved=approve_decision(req,spec['clashes'],answer,scripted=False)
        record.update(requirements_v2=approved,decision=approved['decision'],status='EDITING SERVICE')
        (out/'approved.yaml').write_text(json.dumps(approved,indent=2)+'\n')
        agent_files=copy.deepcopy(files);agent_files['test_policy.py']=approved_visible_tests(approved)
        record['approved_agent_source_sha256']=hash_files(agent_files)
        record['authorized_visible_test_change']={'source':'developer-approved v2, not agent discretion','v1_sha256':hash_files(files)['test_policy.py'],
                                                  'v2_sha256':hash_files(agent_files)['test_policy.py']}
        save()
        changed,agent=edit(agent_files,approved,out,fake=fake_packet['implementation'] if fake_packet else None)
        record['agent']=agent
        for name,data in changed.items():
            target=artifacts/'after'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(data)
        record.update(status='CHECKING HTTP');save()
        final=check(changed,approved);record['final']=final
        record['outcome']=final['outcome'];record['status']='CHECKED' if final['outcome']!='HARNESS ERROR' else 'HARNESS ERROR'
        return record
    except (EOFError,KeyboardInterrupt):
        record['pause_note']='Stopped for the human; no implicit decision or implementation';raise
    except Exception as error:
        record.update(status='HARNESS ERROR',error=type(error).__name__+': '+str(error));raise
    finally:
        if 'agent' not in record and (out/'agent.json').is_file():record['agent']=json.loads((out/'agent.json').read_text())
        rows=receipts();record['provider_receipts']=rows
        record['paid_calls']=sum(r.get('provider_calls',0) for r in rows)
        record['cost_usd']=sum(r['cost_usd'] for r in rows) if all(r.get('cost_usd') is not None for r in rows) else None
        record['cost_complete']=all(r.get('cost_usd') is not None for r in rows)
        record['elapsed_seconds']=round(time.monotonic()-started,3)
        record['runtime_source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('returns_demo','returns_service') for p in (ROOT/folder).glob('*.py')}
        save();provider.RUN_ID.reset(token)
