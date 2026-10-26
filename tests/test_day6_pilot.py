"""Offline safety gates for tomorrow's clean pilot and reviewed freeze."""
import copy,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class PlannedPilotTests(unittest.TestCase):
 def plan(self):return json.loads((ROOT/'study/clean_pilot_plan.json').read_text())
 def test_today_is_refused_before_any_execution(self):
  from muse_guard.pilot import validate_day
  with self.assertRaisesRegex(ValueError,'2026-10-27'):validate_day(self.plan(),'2026-10-26')
  validate_day(self.plan(),'2026-10-27')
 def test_exact_balanced_dev_allocation_only(self):
  from muse_guard.pilot import validate_plan
  plan=self.plan();validate_plan(plan)
  plan['entries'][0]['task']='h01-a'
  with self.assertRaises(ValueError):validate_plan(plan)
  plan=self.plan();plan['entries'][-1]=copy.deepcopy(plan['entries'][0])
  with self.assertRaises(ValueError):validate_plan(plan)
 def test_freeze_refuses_an_incomplete_or_unknown_cost_pilot(self):
  from muse_guard.pilot import freeze_ready
  entry={'task':'retry-impossible','kind':'impossible','mode':'plain','record':None}
  self.assertFalse(freeze_ready([entry]))
  entry['record']={'attempt':{'model_invoked':True,'cost_usd':None,'outcome':'HARNESS ERROR'}}
  self.assertFalse(freeze_ready([entry]))

 def test_refreeze_requires_real_coding_steps_and_valid_checker_evidence(self):
  from muse_guard.pilot import freeze_ready
  row={'model_invoked':True,'cost_usd':.01,'main_steps':2,'outcome':'PASS','cli_version':'Muse Code 1.4.2 (1.4.2-R4684.1)',
       'expected_test_ids':['OriginalTests.a','HiddenTests.a'],'tests':[{'id':'OriginalTests.a','layer':'visible','status':'PASS'},{'id':'HiddenTests.a','layer':'hidden','status':'PASS'}]}
  entries=[{'record':{'status':'PASS','attempt':copy.deepcopy(row)}} for _ in range(12)]
  self.assertTrue(freeze_ready(entries))
  entries[0]['record']['attempt']['tests']=[]
  self.assertFalse(freeze_ready(entries))
  entries[0]['record']['attempt']=dict(row,main_steps=0)
  self.assertFalse(freeze_ready(entries))
  entries[0]['record']['attempt']=dict(row,cli_version='unexpected CLI')
  self.assertFalse(freeze_ready(entries))

 def test_refreeze_rejects_gateway_budget_blocks_even_with_complete_tests(self):
  from muse_guard.pilot import freeze_ready
  row={'model_invoked':True,'cost_usd':.01,'main_steps':1,'outcome':'TASK FAILURE','cli_version':'Muse Code 1.4.2 (1.4.2-R4684.1)',
       'expected_test_ids':['OriginalTests.a','HiddenTests.a'],'tests':[{'id':'OriginalTests.a','layer':'visible','status':'PASS'},{'id':'HiddenTests.a','layer':'hidden','status':'FAIL'}],
       'budget_events':[{'usage':{'input_tokens':1,'output_tokens':1,'cached_input_tokens':0}},{'blocked':True,'block_kind':'budget'}]}
  entries=[{'record':{'status':'TASK FAILURE','attempt':copy.deepcopy(row)}} for _ in range(12)]
  self.assertFalse(freeze_ready(entries))
  for entry in entries:entry['record']['attempt']['budget_events'][-1]['block_kind']='shutdown'
  self.assertTrue(freeze_ready(entries))
