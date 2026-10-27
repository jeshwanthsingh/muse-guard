import copy,json,tempfile,unittest,subprocess,os
from pathlib import Path
from unittest.mock import patch
from submission_tools import restart_study as s,restart_budget as b
ROOT=Path(__file__).resolve().parents[1]
class RehearsalTests(unittest.TestCase):
 def test_actual_repository_root(self):
  self.assertEqual(b.ROOT,ROOT);b.validate_root()
 def test_wrong_root_rejected(self):
  with patch.object(b,'ROOT',ROOT.parent):
   with self.assertRaises(ValueError):b.validate_root()
 def test_outside_output_rejected(self):
  with self.assertRaises(ValueError):b.configure({'budget':'daily','output':'../outside'})
 def test_symlink_output_rejected(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'results/raw') as d:
   link=Path(d)/'escape';link.symlink_to('/private/tmp',target_is_directory=True)
   with self.assertRaises(ValueError):b.inside(link/'cohort.json')
 def test_mismatched_running_total_aborts(self):
  with tempfile.TemporaryDirectory() as d:
   total=Path(d)/'total.json';total.write_text('{"known_cost_usd":0}')
   with patch.object(b,'validate_root'),patch.object(b,'inside',side_effect=lambda p:p),patch.object(b,'TOTAL',total),patch.object(b,'ledger_records',return_value=[{'cost_usd':.32629155}]):
    with self.assertRaisesRegex(ValueError,'differs'):b.self_check()
 def test_receipt_cost_unknown_aborts(self):
  with self.assertRaises(ValueError):b.cost_sum([{'cost_usd':None}])
 def test_interrupted_phase_attached_and_summarized(self):
  from submission_tools.export_runtime import runner
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);entry={'task':'refund-impossible','mode':'plain','kind':'impossible','repeat':1,'record':None}
   def interrupted(task,results,**kw):
    row={'run_id':'interrupted-fixture','cost_usd':.01,'tokens':{'input':1,'output':1,'cached_input':0},'main_steps':None,'interrupted':True,'outcome':'UNKNOWN','original_tests_edited':None,'budget_events':[{'usage':{'input_tokens':1,'output_tokens':1,'cached_input_tokens':0}}]}
    kw['on_start'](row);(root/'interrupted-fixture.json').write_text(json.dumps(row));raise KeyboardInterrupt()
   with patch.object(s,'RESULTS_ROOT',root),patch.object(s,'PLAN',{'split':'dev'}),patch.object(runner,'run_one',side_effect=interrupted),patch.object(s,'save_total',return_value={'known_cost_usd':.01}):
    with self.assertRaises(KeyboardInterrupt):s.flow(entry,lambda:None)
    self.assertEqual(entry['record']['attempt']['cost_usd'],.01)
    out=s.report({'entries':[entry],'status':'STOPPED','freeze':{}})['primary_results']['plain']
    self.assertEqual(out['known_cost_usd'],.01);self.assertEqual(out['unknown_behavior_attempts'],1)
    self.assertIsNone(out['attempts'][0]['behavior']['original_tests_edited']);self.assertTrue(out['attempts'][0]['receipts'])
 def test_sandbox_repo_workspace_secret_and_write_boundary(self):
  from submission_tools.export_policy import author_command
  with tempfile.TemporaryDirectory(dir=ROOT/'results/raw') as d:
   root=Path(d);work=root/'work';work.mkdir();secret=root/'.env';secret.write_text('FAKE_TEST_VALUE')
   code='from pathlib import Path; import sys; Path("inside").write_text("ok"); denied=0\nfor p in sys.argv[1:]:\n try: Path(p).read_text() if p.endswith(".env") else Path(p).write_text("bad")\n except PermissionError: denied+=1\nprint(denied)'
   import sys
   result=subprocess.run(author_command([sys.executable,'-c',code,str(secret),str(root/'outside')],write_root=work),cwd=work,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'2');self.assertTrue((work/'inside').exists())
 def test_reference_gate_with_repo_scratch(self):
  from muse_guard import checker,rule_checker
  from muse_guard.quality_gate import accept_task
  from muse_guard.rules import TASKS
  from submission_tools.export_policy import observe_in_repo
  with tempfile.TemporaryDirectory(dir=ROOT/'results/raw') as d,patch.object(tempfile,'tempdir',d),patch.object(checker,'_observe',observe_in_repo),patch.object(rule_checker,'_observe',observe_in_repo):
   for name in ('refund-solvable','refund-impossible'):
    self.assertEqual(accept_task(TASKS[name])['status'],'ACCEPTED')
 def test_candidate_cannot_read_repo_env_in_repo_scratch(self):
  from submission_tools.export_policy import observe_in_repo
  with tempfile.TemporaryDirectory(dir=ROOT/'results/raw') as d,patch.object(tempfile,'tempdir',d):
   p=Path(d);(p/'.env').write_text('FAKE');source=p/'solution.py'
   source.write_text('def solve(x):\n try:\n  open('+repr(str(p/'.env'))+').read()\n  return False\n except PermissionError: return True\n')
   self.assertTrue(observe_in_repo(source,{}))
if __name__=='__main__':unittest.main()
