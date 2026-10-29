"""Local test build: fake model responses, no Meta calls.

Run from the repo root: uvicorn live_demo.local_dev:app --port 8765
"""
import json

from spec_guard.core import sentences
from live_demo.app import HERE, create_app

SAMPLES = json.loads((HERE / 'samples.json').read_text())


def fake_response(proposal):
    body = {'status': 'completed',
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(proposal)}]}],
            'usage': {'input_tokens': 300, 'output_tokens': 200, 'input_tokens_details': {'cached_tokens': 0}}}
    return json.dumps(body).encode()


def fake_model(payload):
    for sample in SAMPLES:
        if sample['doc'] == payload['input']:
            return fake_response(sample['proposal'])
    first = next(iter(sentences(payload['input'])), '')
    return fake_response({'input_space': {'flag': [True, False]}, 'rules': [],
                          'unconverted': [{'quote': first, 'reason': 'Fake local model did not convert this'}]})


app = create_app(fake_model, {}, mode='test')
