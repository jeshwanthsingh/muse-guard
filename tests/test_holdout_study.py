import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
from submission_tools import holdout_study as study
from submission_tools.study_runtime import ledger
from submission_tools.study_runtime import runner,card
class StudyTests(unittest.TestCase):
 def test_exact_allocation_and_seed(self):
  rows=study.allocation();self.assertEqual(rows,study.allocation());self.assertEqual(len(rows),160)
  self.assertEqual(len({(r['task'],r['mode'],r['repeat']) for r in rows}),160)
  for mode in ('plain','guarded'):
   selected=[r for r in rows if r['mode']==mode]
   self.assertEqual(len(selected),80);self.assertEqual(sum(r['kind']=='impossible' for r in selected),40)
   self.assertEqual(len({r['task'] for r in selected}),40)
 def test_exact_cap_and_unknown(self):
  ledger.reserve_budget([{'cost_usd':69}],1)
  for rows,amount in [([{'cost_usd':69}],1.00000001),([{'cost_usd':None,'accounted_upper_bound_usd':1}],1),([{'cost_usd':-1}],1)]:
   with self.assertRaises(ValueError):ledger.reserve_budget(rows,amount)
 def test_ledger_never_resets_at_midnight_or_counts_wrappers(self):
  with tempfile.TemporaryDirectory() as d,patch.object(ledger,'RESULTS_ROOT',Path(d)):
   Path(d,'a.json').write_text(json.dumps({'run_id':'a','date':'2026-10-27','cost_usd':40}))
   Path(d,'b.json').write_text(json.dumps({'run_id':'b','date':'2026-10-28','cost_usd':29}))
   Path(d,'wrapper.json').write_text(json.dumps({'cost_usd':69}))
   rows=ledger.ledger_records(d,'2026-10-29');self.assertEqual(len(rows),2)
   self.assertEqual(ledger.save_total(d)['known_cost_usd'],69)
 def test_faults_stop_but_candidate_failure_is_outcome(self):
  row={'cost_usd':.1,'model_invoked':True,'cli_version':'Muse Code 1.4.2 (1.4.2-R4684.1)','export_exit_code':0,'main_steps':2,'outcome':'TASK FAILURE','expected_test_ids':['a','b'],'tests':[{'id':'a','layer':'visible','status':'FAIL'},{'id':'b','layer':'hidden','status':'ERROR'}]}
  self.assertIsNone(study.phase_failure(row))
  for change in ({'cost_usd':None},{'outcome':'HARNESS ERROR'},{'budget_events':[{'blocked':True,'block_kind':'policy'}]},{'export_exit_code':1},{'model_invoked':False},{'cli_version':'other'},{'tests':[]}):
   self.assertIsNotNone(study.phase_failure(dict(row,**change)))
 def test_card_fault_blocks_before_repair(self):
  task=study.TASKS['retry-impossible'];req=task['requirements'];w={'method':'POST','status':429,'idempotent':False}
  attempt={'run_id':'a','outcome':'CONFLICT VERIFIED','cost_usd':.1,'conflict_report':{'conflict':True,'rules':['A','B'],'witness':w,'explanation':'fake'}}
  with tempfile.TemporaryDirectory() as d,patch.object(study,'RESULTS_ROOT',Path(d)),patch.object(runner,'run_one',return_value=attempt) as run,patch.object(card,'conflict_card',return_value={'run_id':'c','status':'HARNESS ERROR','cost_usd':0}),patch.object(study,'phase_failure',side_effect=[None,'card failure']):
   entry={'task':'retry-impossible','mode':'guarded','repeat':1}
   with self.assertRaises(study.StudyStop):study.flow(entry,lambda:None)
   self.assertEqual(run.call_count,1);self.assertEqual(entry['record']['status'],'STOPPED')
 def test_existing_cohort_prevents_all_execution(self):
  with tempfile.TemporaryDirectory() as d,patch.object(study,'RESULTS_ROOT',Path(d)),patch.object(study,'COHORT',Path(d)/'cohort.json'),patch.object(study,'verify_freeze',return_value={}):
   Path(d,'cohort.json').write_text('{}')
   with self.assertRaisesRegex(ValueError,'already started'):study.execute()
 def test_execution_stops_at_first_fault(self):
  with tempfile.TemporaryDirectory() as d,patch.object(study,'RESULTS_ROOT',Path(d)),patch.object(ledger,'RESULTS_ROOT',Path(d)),patch.object(study,'COHORT',Path(d)/'cohort.json'),patch.object(study,'verify_freeze',return_value={}),patch.object(study,'flow',side_effect=study.StudyStop('test fault')) as flow:
   result=study.execute();self.assertEqual(flow.call_count,1);self.assertEqual(result['status'],'STOPPED')
 def test_reused_runtime_prompts_limits_and_separate_gateway(self):
  from submission_tools.settlement import ReconciledGateway
  self.assertIs(runner.Gateway,ReconciledGateway);self.assertIs(card.Gateway,ReconciledGateway)
  from muse_guard.tasks import prompt
  self.assertIs(runner.prompt,prompt)
  self.assertEqual(ledger.CAP,Decimal(70))
