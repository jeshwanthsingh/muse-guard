import json,unittest
from pathlib import Path
from decimal import Decimal
from muse_guard.gateway import DollarBudget
from submission_tools.settlement import PhaseSettlement,ReconciledGateway
ROOT=Path(__file__).resolve().parents[1]
class SettlementTests(unittest.TestCase):
 def test_replay_actual_shipping_receipts_old_fails_new_settles(self):
  events=json.loads((ROOT/'results/shipping-impossible-v2-3c5f60d5f05a.json').read_text())['budget_events']
  old=DollarBudget('1.36');new=PhaseSettlement('1.36')
  calls=[e for e in events if not e.get('blocked')]
  for n,e in enumerate(calls):
   old.admit(e['input_tokens_reserved'],e['max_output_tokens'])
   if n==4:
    with self.assertRaisesRegex(ValueError,'exceeded request'):old.settle(e['usage'])
   else:old.settle(e['usage'])
   new.admit(e['input_tokens_reserved'],e['max_output_tokens']);new.settle(e['usage'])
  self.assertEqual(new.spent,Decimal('0.04245365'));self.assertFalse(new.unknown)
  self.assertEqual(new.admit(1000,2048),2048)
 def test_unknown_usage_still_blocks(self):
  b=PhaseSettlement(1);b.admit(1,1);b.settle(None)
  with self.assertRaises(ValueError):b.admit(1,1)
 def test_phase_quota_still_blocks_and_accounts_known_overrun(self):
  b=PhaseSettlement('.001');b.admit(1,1)
  with self.assertRaisesRegex(ValueError,'phase dollar'):b.settle({'input_tokens':1,'output_tokens':1000,'cached_input_tokens':0})
  self.assertGreater(b.spent,b.limit)
  with self.assertRaises(ValueError):b.admit(1,1)
 def test_admission_never_expands_quota(self):
  b=PhaseSettlement('.001')
  with self.assertRaises(ValueError):b.admit(10000,2048)
 def test_token_overrun_is_accounted_and_stops(self):
  g=ReconciledGateway('fake',token_limit=10,dollar_limit=1)
  u={'input_tokens':2,'output_tokens':20,'cached_input_tokens':0}
  g.events=[{'usage':u}];g.dollars.admit(2,3)
  with self.assertRaisesRegex(ValueError,'token budget'):g.dollars.settle(u)
  self.assertTrue(g.dollars.unknown);self.assertEqual(g.budget.reserved_tokens,22)

 def test_gateway_forwards_after_known_small_overrun(self):
  import urllib.request
  calls=[]
  def transport(path,data):
   if path.endswith('input_tokens'):return {'input_tokens':6929}
   calls.append(data)
   return {'status':'completed','usage':{'input_tokens':6786,'output_tokens':2120,'input_tokens_details':{'cached_tokens':0}}}
  with ReconciledGateway('fake',token_limit=320000,dollar_limit='1.36',transport=transport) as g:
   for _ in range(2):
    req=urllib.request.Request(g.url+'/responses',data=json.dumps({'model':'muse-spark-1.3','input':'fake'}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as response:self.assertEqual(response.status,200)
   self.assertEqual(len(calls),2);self.assertFalse(any(e.get('blocked') for e in g.events))
   self.assertTrue(g.events[0]['settlement']['exceeded_request_estimate'])
