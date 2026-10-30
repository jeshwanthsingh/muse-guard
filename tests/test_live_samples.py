import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from live_demo.app import create_app
class LiveSampleLabelTests(unittest.TestCase):
 def setUp(self):
  self.samples=json.loads((ROOT/'live_demo/samples.json').read_text())
  self.client=TestClient(create_app(None,{},mode='test'))
 def test_every_sample_label_matches_its_record(self):
  for s in self.samples:
   record=json.loads((ROOT/s['source']['run']).read_text())
   self.assertEqual(s['response_kind'],record['response_kind'],s['id'])
   expected='recorded extraction' if record['response_kind']=='real' else 'constructed example (not a real model output)'
   self.assertEqual(s['label'],expected,s['id'])
 def test_approved_evidence_matches_sample_response_kind(self):
  for s in self.samples:
   item=[x for x in self.client.get('/samples').json()['samples'] if x['id']==s['id']][0]
   dec={i['key']:True for i in item['view']['items'] if i['valid']}
   chk=self.client.post('/api/check',json={'doc':s['doc'],'proposal':s['proposal'],'decisions':dec}).json()
   w={'+'.join(g['rules']):g['rules'][0] for g in chk['clashes']}
   ap=self.client.post('/api/approve',json={'doc':s['doc'],'proposal':s['proposal'],'decisions':dec,'winners':w})
   self.assertEqual(ap.status_code,200,ap.text)
   self.assertEqual(ap.json()['approved_rules']['spec_origin']['response_kind'],s['response_kind'],s['id'])
   self.assertEqual(ap.json()['evidence']['model_responses'],'recorded %s extraction'%s['response_kind'],s['id'])
 def test_page_status_text_matches_real_samples(self):
  html=(ROOT/'live_demo/static/index.html').read_text()
  if any(s['response_kind']=='real' for s in self.samples):
   self.assertIn('Loaded a recorded extraction from a saved real run',html)
if __name__=='__main__':unittest.main()
