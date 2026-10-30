"""Build samples.json from saved real Spark extractions. No model calls.

HTTP retry is not here on purpose: no saved real extraction exists for it.
Package room is not here on purpose: 3 of its saved rules did not match their quotes exactly,
so approval is blocked (see docs/EXTRACTION_FAILURES.md, Known limitation).
"""
import hashlib
import json
from pathlib import Path

from spec_guard.core import digest

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'samples.json'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def sample(sample_id, title, doc, proposal, proposal_sha, doc_sha, run, model, cost, response_kind):
    assert sha(doc) == doc_sha and digest(proposal) == proposal_sha
    return {'id': sample_id, 'title': title, 'doc': doc, 'doc_sha256': doc_sha, 'proposal': proposal,
            'label': 'recorded extraction', 'response_kind': response_kind,
            'source': {'run': run, 'model': model, 'cost_usd': cost}}


def refunds():
    run = 'spec_eval/results/2026-10-27/refunds/record.json'
    record = json.loads((ROOT / run).read_text())
    assert record['response_kind'] == 'real'
    return sample('refunds', 'Refund notes', record['doc'], record['proposal'], record['proposal_sha256'],
                  record['doc_sha256'], run, record['model'], record['cost']['cost_usd'], record['response_kind'])


if __name__ == '__main__':
    samples = [refunds()]
    OUT.write_text(json.dumps(samples, indent=2, ensure_ascii=False) + '\n')
    print('wrote', len(samples), 'samples to', OUT.name)
