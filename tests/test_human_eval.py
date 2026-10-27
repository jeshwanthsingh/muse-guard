import copy,json,unittest
from pathlib import Path
from submission_tools.human_eval import score,document
from spec_guard.core import review
ROOT=Path(__file__).resolve().parents[1]/'spec_eval/human'
class HumanEvalTests(unittest.TestCase):
 def fixture(self,n):return (ROOT/f'doc{n}.md').read_text(),json.loads((ROOT/'truth'/f'doc{n}.json').read_text())
 def test_approved_keys_and_clash_counts(self):
  for n,count in ((1,4),(2,0)):
   doc,t=self.fixture(n);m,r=score(doc,t['proposal'],t)
   self.assertTrue(m['success']);self.assertEqual(m['clashes_found'],count);self.assertFalse(r['uncovered_inputs'])
 def test_optional_fallback_does_not_hide_missing_package_rule(self):
  doc,t=self.fixture(2);p=copy.deepcopy(t['proposal']);p['rules'].pop()
  m,r=score(doc,p,t);self.assertFalse(m['success']);self.assertEqual(m['rules_missing'],1)
 def test_invented_default_is_wrong(self):
  doc,t=self.fixture(2);p=copy.deepcopy(t['proposal']);p['default']={'quote':'Otherwise hold it.','action':'hold'}
  m,_=score(doc,p,t);self.assertFalse(m['success']);self.assertEqual(m['rules_wrong'],1)
 def test_invented_quote_and_changed_domain_fail(self):
  doc,t=self.fixture(1);p=copy.deepcopy(t['proposal']);p['rules'][0]['quote']='Invented.';p['input_space']['heard_back']=[True]
  m,_=score(doc,p,t);self.assertFalse(m['success']);self.assertFalse(m['domains_correct'])
 def test_fixed_aliases_and_linewraps(self):
  doc,t=self.fixture(2);p=copy.deepcopy(t['proposal']);p['rules'][0]['action']='return'
  p['rules'][1]['quote']=p['rules'][1]['quote'].replace('notify the resident right away.','notify the resident\nright away.')
  m,_=score(doc,p,t);self.assertTrue(m['success'])

 def test_alias_collision_fails_without_silently_dropping_field(self):
  doc,t=self.fixture(2);p=copy.deepcopy(t['proposal']);p['input_space']['is_perishable']=[False,True]
  m,_=score(doc,p,t);self.assertFalse(m['success']);self.assertGreater(m['schema_errors'],0)
 def test_real_scoring_retains_provenance(self):
  doc,t=self.fixture(2);m,r=score(doc,t['proposal'],t,response_kind='real',cost={'model_invoked':True,'cost_usd':.001})
  self.assertEqual(r['response_kind'],'real');self.assertTrue(r['cost']['model_invoked'])
