import base64,copy,json,re,tempfile,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from returns_demo.flow import run,SCOPE
from returns_demo.source import ROOT,baseline_files
from returns_demo.view import witness_response


def fake():return json.loads((ROOT/'demo/returns-service/fake-response.json').read_text())

class ReturnsFlowTests(unittest.TestCase):
 def execute(self,packet=None):
  with tempfile.TemporaryDirectory() as d,redirect_stdout(StringIO()):
   out=Path(d)/'run';r=run(out,fake_packet=packet or fake());page=(out/'index.html').read_text()
   self.assertEqual(json.loads((out/'run.json').read_text()),r)
  return r,page
 def test_fake_end_to_end_modifies_service_and_http_rechecks_all_cases(self):
  with patch('returns_demo.provider.propose',side_effect=AssertionError('No paid calls')),patch('returns_demo.provider.phase',side_effect=AssertionError('No paid calls')):
   r,page=self.execute()
  self.assertEqual(r['status'],'CHECKED');self.assertEqual(r['outcome'],'PASS');self.assertEqual(r['cost_usd'],0);self.assertEqual(r['paid_calls'],0)
  self.assertEqual(r['baseline']['outcome'],'PASS');self.assertEqual(len(r['final']['tests']),11);self.assertTrue(r['final']['inventory_complete'])
  self.assertEqual(witness_response(r['baseline'])['json']['next_action'],'refund_immediately');self.assertEqual(witness_response(r['final'])['json']['next_action'],'manual_review')
  self.assertEqual(r['requirements_v1']['version'],1);self.assertEqual(r['requirements_v2']['version'],2);self.assertEqual(r['decision']['winner'],'B')
  self.assertEqual(r['baseline']['regression_source_sha256'],r['final']['regression_source_sha256'])
  self.assertEqual(r['baseline_source_sha256']['server.py'],r['agent']['source_sha256']['server.py']);self.assertNotEqual(r['baseline_source_sha256']['refund_policy.py'],r['agent']['source_sha256']['refund_policy.py'])
  self.assertEqual(r['decision_preview']['groups'][0]['affected_inputs'],1)
  for text in ('Fake model responses','actual HTTP response','1 conflict (A vs B), 1 input affected','A wins','B wins','Rule B wins','Actual source diff','before → after',SCOPE,'Download evidence record'):
   self.assertIn(text,page)
  self.assertNotRegex(page,r'<(?:script|form|button)\b')
  payload=re.search(r'data:application/json;base64,([^"]+)',page).group(1);self.assertEqual(json.loads(base64.b64decode(payload)),r)
 def test_wrong_code_and_edited_tests_fail_real_http_not_fake_claims(self):
  p=fake();p['implementation']['claim']='Everything is complete and all tests passed.';p['implementation']['files']={'refund_policy.py':'def next_action(x): return "refund_immediately"\n','test_existing.py':'assert True\n','test_policy.py':'assert True\n'}
  r,page=self.execute(p);self.assertEqual(r['outcome'],'FAIL');self.assertTrue(r['agent']['original_tests_edited']);self.assertEqual(len(r['final']['tests']),11)
 def test_rejecting_any_rule_stops_before_service_edit(self):
  p=fake();p['review'][0]=False
  with patch('returns_demo.flow.edit') as edit:
   r,_=self.execute(p)
  self.assertEqual(r['status'],'REVIEW REJECTED');edit.assert_not_called();self.assertNotIn('decision',r)
 def test_eof_at_decision_retains_pause_without_implicit_choice(self):
  p=fake()
  # Real-path review is exercised with a fake extraction; provider/date mocked,
  # but implementation remains forbidden until actual explicit input.
  with tempfile.TemporaryDirectory() as d,redirect_stdout(StringIO()),patch('returns_demo.provider.require_real_date'),patch('returns_demo.provider.propose',return_value=(p['proposal'],{'cost_usd':0,'model_invoked':False})),patch('returns_demo.flow.edit') as edit:
   out=Path(d)/'run'
   def wait(prompt):raise EOFError
   with self.assertRaises(EOFError):run(out,reviewer=lambda item:True,input_fn=wait)
   r=json.loads((out/'run.json').read_text());self.assertEqual(r['status'],'AWAITING DECISION');self.assertNotIn('decision',r);edit.assert_not_called()
 def test_real_mode_is_blocked_today_before_any_provider_call(self):
  with tempfile.TemporaryDirectory() as d,patch('returns_demo.provider.today',return_value='2026-10-28'),patch('returns_demo.provider.ReconciledGateway') as gate:
   out=Path(d)/'run'
   with self.assertRaisesRegex(ValueError,'No paid calls today'):run(out)
   self.assertFalse(out.exists());gate.assert_not_called()
 def test_no_automatic_accept_or_priority_flags_exist(self):
  from returns_demo.cli import main
  for flag in ('--accept-all','--decide'):
   with self.subTest(flag=flag),patch('returns_demo.cli.run') as execute,patch('sys.stderr',new=StringIO()):
    with self.assertRaises(SystemExit):main(['--real','--out','unused',flag])
    execute.assert_not_called()
 def test_zero_missing_duplicate_or_skipped_checker_rows_never_pass(self):
  from returns_demo.checker import check,REGRESSIONS
  files=baseline_files();valid=[{'id':'policy.test_case_'+str(i),'status':'PASS'} for i in range(4)]+[{'id':'regression.'+name,'status':'PASS'} for name in REGRESSIONS]
  skipped=copy.deepcopy(valid);skipped[0]['status']='SKIP'
  for rows in ([],valid[:-1],valid+[valid[0]],skipped):
   with self.subTest(size=len(rows)),patch('returns_demo.checker.checker_run',return_value={'outcome':'PASS','tests':rows,'http':[]}):
    self.assertEqual(check(files)['outcome'],'HARNESS ERROR')
 def test_unapproved_requirements_cannot_regenerate_tests_or_change_checker_expectations(self):
  from returns_demo.checker import check
  from returns_demo.flow import approved_visible_tests
  with self.assertRaisesRegex(ValueError,'approved v2'):approved_visible_tests({'version':2})
  with self.assertRaisesRegex(ValueError,'Approved'):check(baseline_files(),{'version':2})
