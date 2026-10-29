"""Build samples.json from saved real Spark extractions. No model calls.

HTTP retry is not here on purpose: no saved real extraction exists for it.
"""
import hashlib
import json
from pathlib import Path

from spec_guard.core import digest, validate

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'samples.json'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def sample(sample_id, title, doc, proposal, proposal_sha, doc_sha, run, model, cost):
    assert sha(doc) == doc_sha and digest(proposal) == proposal_sha
    return {'id': sample_id, 'title': title, 'doc': doc, 'doc_sha256': doc_sha, 'proposal': proposal,
            'label': 'recorded extraction',
            'source': {'run': run, 'model': model, 'cost_usd': cost}}


def refunds():
    run = 'spec_eval/results/2026-10-27/refunds/record.json'
    record = json.loads((ROOT / run).read_text())
    assert record['response_kind'] == 'real'
    return sample('refunds', 'Refund notes', record['doc'], record['proposal'], record['proposal_sha256'],
                  record['doc_sha256'], run, record['model'], record['cost']['cost_usd'])


def package_room():
    run = 'spec_eval/human/results/2026-10-27/evaluation.json'
    entry = json.loads((ROOT / run).read_text())['entries'][1]
    review = entry['normalized_review']
    # The normalized review stores a re-spelled copy of the text; the source file is the exact input.
    doc = (ROOT / 'spec_eval/human/doc2.md').read_bytes().decode()
    assert review['response_kind'] == 'real' and sha(doc) == entry['source_sha256']
    assert not validate(doc, entry['proposal'])['errors']
    return sample('package-room', 'Package room rules', doc, entry['proposal'], review['proposal_sha256'],
                  entry['source_sha256'], run, entry['cost']['model'], entry['cost']['cost_usd'])


if __name__ == '__main__':
    samples = [refunds(), package_room()]
    OUT.write_text(json.dumps(samples, indent=2, ensure_ascii=False) + '\n')
    print('wrote', len(samples), 'samples to', OUT.name)
