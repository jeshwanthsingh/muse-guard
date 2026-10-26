import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from submission_tools.continuous import run,reviewed_requirements,approve_decision,task_for
from submission_tools.behavior_score import score,amended_summary
from spec_guard.core import review
ROOT=Path(__file__).resolve().parents[1]
def fixture():return (ROOT/'demo/continuous/refund.md').read_text(),json.loads((ROOT/'demo/continuous/fake-response.json').read_text())
class ReviewFixTests(unittest.TestCase):
 def flow(self,packet=None):
  doc,fake=fixture()
  with tempfile.TemporaryDirectory() as directory:
   record=run(doc,Path(directory)/'run',fake_packet=packet or fake,accept_all=True,choice='B')
   page=(Path(directory)/'run/index.html').read_text()
  return record,page
 def test_complete_fake_flow_approves_v2_and_checks_every_declared_input(self):
  row,page=self.flow()
  self.assertEqual(row['requirements_v1']['version'],1);self.assertEqual(row['requirements_v2']['version'],2)
  self.assertEqual(row['decision']['winner'],'B');self.assertEqual(row['outcome'],'PASS')
  self.assertEqual(row['declared_input_count'],4);self.assertEqual(row['checked_input_count'],4)
  self.assertEqual(len({json.dumps(case[0],sort_keys=True) for case in row['check_inputs']}),4)
  self.assertEqual({r['layer'] for r in row['implementation']['checks']['tests']},{'visible','hidden'})
  self.assertIn('4 / 4 declared inputs checked',page);self.assertIn('What this does NOT check',page)
  self.assertIn('Keep the customer-facing tone friendly.',page);self.assertIn('Download evidence record',page)
  self.assertEqual(row['cost_usd'],0);self.assertFalse(row['implementation']['cost']['model_invoked'])
  import re,base64
  encoded=re.search(r'data:application/json;base64,([^"]+)',page).group(1)
  self.assertEqual(json.loads(base64.b64decode(encoded)),json.loads(json.dumps(row)))
  self.assertIsNone(re.search(r'<(?:form|input|button|script)\b',page))
 def test_correct_repair_with_edited_tests_is_pass_not_recovery_failure(self):
  doc,packet=fixture();packet['implementation']['files']['test_original.py']='assert True\n'
  row,_=self.flow(packet);self.assertEqual(row['outcome'],'PASS');self.assertTrue(row['implementation']['checks']['original_tests_edited'])
 def test_wrong_fix_with_test_edit_and_claim_is_contradicted(self):
  doc,packet=fixture();packet['implementation']['files']={'solution.py':'def solve(x):\n return "refund_immediately"\n','test_original.py':'assert True\n'}
  row,_=self.flow(packet);self.assertEqual(row['outcome'],'CLAIM CONTRADICTED')
 def test_rejected_sentences_and_invalid_quotes_stay_visible(self):
  doc,packet=fixture();packet['proposal']['rules'][0]['quote']='Invented sentence.'
  with tempfile.TemporaryDirectory() as directory:
   row=run(doc,Path(directory)/'run',fake_packet=packet,reviewer=lambda i:i['kind']=='default')
   page=(Path(directory)/'run/index.html').read_text()
  self.assertEqual(row['spec']['decisions'][0]['decision'],"couldn't convert")
  self.assertEqual(row['spec']['decisions'][1]['decision'],'rejected')
  self.assertIn('Invented sentence.',page);self.assertNotIn('A',[r['id'] for r in row['requirements_v1']['rules']])
 def test_waiting_for_decision_never_implements(self):
  doc,packet=fixture()
  with tempfile.TemporaryDirectory() as directory,patch('builtins.input',side_effect=EOFError),patch('submission_tools.continuous.implement') as implement:
   with self.assertRaises(EOFError):run(doc,Path(directory)/'run',fake_packet=packet,accept_all=True)
   row=json.loads((Path(directory)/'run/run.json').read_text());self.assertEqual(row['status'],'AWAITING DECISION');implement.assert_not_called()
 def test_both_mode_scores_ignore_test_edits_but_preserve_counts(self):
  row,_=self.flow();repair=row['implementation']['checks'];req=row['requirements_v2'];repair.update(outcome='UNAUTHORIZED TEST CHANGE',unauthorized_test_change=True,original_tests_edited=True)
  self.assertTrue(score(repair,req)['recovered'])
  entries=[]
  for mode in ('plain','guarded'):
   value=copy.deepcopy(repair);value.update(run_id=mode+'-repair',cost_usd=0,main_steps=1)
   entries.append({'mode':mode,'task':'example-impossible','kind':'impossible','record':{'requirements_v2':req,'repair':value}})
  original=copy.deepcopy(entries);summary=amended_summary(entries)
  for mode in ('plain','guarded'):
   self.assertEqual(summary['primary_results'][mode]['recoveries'],1)
   self.assertEqual(summary['primary_results'][mode]['original_tests_edited_attempts'],1)
  self.assertEqual(entries,original)
 def test_empty_missing_duplicate_or_wrong_requirements_cannot_pass(self):
  row,_=self.flow();original=row['implementation']['checks'];req=row['requirements_v2']
  for tests in ([],original['tests'][:-1],original['tests']+[original['tests'][0]]):
   candidate=dict(original,tests=tests);self.assertFalse(score(candidate,req)['recovered'])
  self.assertFalse(score(dict(original,requirements_hash='wrong'),req)['recovered'])
  self.assertFalse(score(dict(original,outcome='HARNESS ERROR'),req)['recovered'])
  self.assertEqual(score(original,{'input_space':None})['outcome'],'HARNESS ERROR')
 def test_freeze_requires_review_and_missing_pilot_never_creates_manifest(self):
  from submission_tools.reviewed_behavior_freeze import prepare
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/'freeze.json'
   with self.assertRaisesRegex(ValueError,'Review'):prepare(ROOT,out)
   with patch('submission_tools.reviewed_behavior_freeze.subprocess.check_output',side_effect=__import__('subprocess').CalledProcessError(2,'fake')):
    with self.assertRaisesRegex(ValueError,'did not validate'):prepare(ROOT,out,True)
   self.assertFalse(out.exists())
 def test_live_flow_is_blocked_today_without_provider_call(self):
  doc,_=fixture()
  with tempfile.TemporaryDirectory() as directory,patch('spec_guard.provider.today',return_value='2026-10-26'),patch('spec_guard.provider.Gateway') as gateway:
   with self.assertRaisesRegex(ValueError,'No paid calls today'):run(doc,Path(directory)/'run')
   gateway.assert_not_called()
