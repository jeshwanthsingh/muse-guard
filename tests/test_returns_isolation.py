import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from returns_demo.source import baseline_files
from returns_demo.checker import check,INPUTS
from returns_demo.preflight import prove
from returns_demo.isolation import environment

class ReturnsIsolationTests(unittest.TestCase):
 def test_baseline_http_passes_all_four_cases_and_unchanged_regressions(self):
  r=check(baseline_files());self.assertEqual(r['outcome'],'PASS');self.assertEqual(len(r['tests']),11);self.assertTrue(r['inventory_complete'])
  self.assertEqual(len(r['http']),31)
 def test_candidate_and_checker_real_sandbox_boundaries_with_planted_env(self):
  with patch.dict(os.environ,{'META_API_KEY':'planted-meta-only','BASETEN_API_KEY':'planted-baseten-only','RETURNS_PLANTED_SECRET':'planted-other-value'}):
   r=prove()
  self.assertEqual(r['status'],'PASS');self.assertTrue(all(v for role in r['checks'].values() for v in role.values()))
 def test_clean_environment_is_allowlisted_for_every_dotenv_value(self):
  with patch.dict(os.environ,{'ARBITRARY_DOTENV_VALUE':'planted-only','META_API_KEY':'planted-only'}):
   env=environment(Path('/tmp/service'))
  self.assertEqual(set(env),{'PATH','HOME','TMPDIR','LANG'});self.assertNotIn('planted-only',str(env))
 def test_edited_tests_cannot_hide_wrong_policy(self):
  files=baseline_files();files['refund_policy.py']=b'def next_action(x): return "refund_immediately"\n';files['test_existing.py']=b'assert True\n';files['test_policy.py']=b'assert True\n'
  r=check(files);self.assertEqual(r['outcome'],'FAIL');self.assertEqual(len(r['tests']),11);self.assertTrue(any(t['status']=='FAIL' for t in r['tests'] if t['id'].startswith('policy.')))
 def test_broken_service_is_never_a_pass(self):
  files=baseline_files();files['server.py']=b'print("all tests passed")\n'
  r=check(files);self.assertEqual(r['outcome'],'HARNESS ERROR');self.assertEqual(r['tests'],[])
 def test_client_refuses_external_urls_and_does_not_follow_redirects(self):
  from returns_demo.check_driver import EndpointClient
  client=EndpointClient(12345)
  with patch('returns_demo.check_driver.http.client.HTTPConnection') as connection:
   for path in ('https://example.invalid/','//example.invalid','/returns?url=anything','/../outside'):
    with self.assertRaises(ValueError):client.request('GET',path)
   connection.assert_not_called()
   response=connection.return_value.getresponse.return_value;response.status=302;response.getheader.return_value='application/json';response.read.return_value=b'{"error":"redirect"}'
   self.assertEqual(client.request('GET','/health')[0],302)
   self.assertEqual(connection.call_count,1);self.assertEqual(connection.call_args.args[:2],('127.0.0.1',12345))
