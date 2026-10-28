from contextlib import contextmanager
import json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
from returns_demo import provider
from returns_demo.agent import edit
from returns_demo.source import baseline_files

class ReturnsProviderTests(unittest.TestCase):
 def test_shared_daily_cap_blocks_before_gateway(self):
  with tempfile.TemporaryDirectory() as d,patch.object(provider,'RESULTS',Path(d)),patch.object(provider,'today',return_value='2026-10-29'),patch.dict(os.environ,{'META_API_KEY':'planted-only'}),patch.object(provider,'ReconciledGateway') as gateway:
   (Path(d)/'prior.json').write_text(json.dumps({'run_id':'prior','date':'2026-10-29','cost_usd':4.999}))
   token=provider.RUN_ID.set('fake-service')
   try:
    with self.assertRaises(ValueError):
     with provider.phase('extract',6144):pass
   finally:provider.RUN_ID.reset(token)
   gateway.assert_not_called()
 def test_all_request_usage_including_reminders_is_recorded_from_first_call(self):
  events=[{'usage':{'input_tokens':100,'output_tokens':10,'cached_input_tokens':0}}, {'usage':{'input_tokens':80,'output_tokens':5,'cached_input_tokens':40}}]
  gateway=MagicMock();gateway.events=events
  with tempfile.TemporaryDirectory() as d,patch.object(provider,'RESULTS',Path(d)),patch.object(provider,'today',return_value='2026-10-29'),patch.dict(os.environ,{'META_API_KEY':'planted-only'}),patch.object(provider,'ReconciledGateway') as cls:
   cls.return_value.__enter__.return_value=gateway
   token=provider.RUN_ID.set('fake-service')
   try:
    with provider.phase('extract',6144) as (g,row):self.assertEqual(g,gateway)
   finally:provider.RUN_ID.reset(token)
   self.assertEqual(row['provider_calls'],2);self.assertEqual(row['tokens'],{'input':180,'output':15,'cached_input':40})
   self.assertAlmostEqual(row['cost_usd'],.00024475)
   self.assertEqual(row['service_run_id'],'fake-service');self.assertNotIn('planted-only',json.dumps(row))
   saved=json.loads((Path(d)/(row['run_id']+'.json')).read_text());self.assertEqual(saved,row)
 def test_real_agent_path_offline_uses_proxy_key_and_clean_child_environment(self):
  from types import SimpleNamespace
  @contextmanager
  def fake_phase(kind,tokens):
   yield SimpleNamespace(url='http://127.0.0.1:12345/v1'),{'cost_usd':.01,'model_invoked':True,'provider_calls':2}
  seen=[]
  def fake_process(args,workspace,env,**kwargs):
   seen.append((args,env,kwargs));(workspace/'refund_policy.py').write_text('def next_action(x): return "manual_review"\n')
   return subprocess.CompletedProcess(args,0,'','')
  def fake_export(cli,session,destination,workspace,env):
   destination.write_text('{}');return SimpleNamespace(returncode=0,diagnostics={'stderr_file':'session.stderr.log'})
  with tempfile.TemporaryDirectory() as d,patch('returns_demo.agent.require_real_date'),patch('returns_demo.agent.shutil.which',return_value='/usr/local/bin/muse'),patch('returns_demo.agent.phase',fake_phase),patch('returns_demo.agent.run_process',side_effect=fake_process),patch('returns_demo.agent.export_session',side_effect=fake_export),patch('returns_demo.agent.session_evidence',return_value={'agent_message':'Recorded mock reply'}),patch.dict(os.environ,{'META_API_KEY':'planted-only','OTHER_ENV_SECRET':'another-planted-only'}):
   files,meta=edit(baseline_files(),{'version':2},Path(d))
  self.assertTrue(seen);self.assertNotIn('planted-only',str(seen));self.assertEqual(seen[0][2]['input_data'],b'proxy-only-no-provider-key\n')
  self.assertEqual(meta['export_exit_code'],0);self.assertIn('refund_policy.py',meta['source_sha256'])
