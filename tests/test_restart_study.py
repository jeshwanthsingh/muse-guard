import json,tempfile,unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from submission_tools import restart_study as study,restart_budget as budget
class RestartTests(unittest.TestCase):
 def test_order_identical(self):
  rows=json.loads((study.ROOT/'study/HOLDOUT_ALLOCATION-2026-10-27.json').read_text())
  self.assertEqual(rows,study.allocation());self.assertEqual(len(rows),160)
 def test_prior_cost_and_no_midnight_reset(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);old=root/'old';new=root/'new';old.mkdir();new.mkdir()
   (old/'one.json').write_text(json.dumps({'run_id':'old','cost_usd':.1083648,'date':'2026-10-27'}))
   (new/'two.json').write_text(json.dumps({'run_id':'new','cost_usd':68,'date':'2026-10-28'}))
   with patch.object(budget,'PRIOR_ROOT',old),patch.object(budget,'RESULTS_ROOT',new):
    rows=budget.ledger_records(new);self.assertEqual(len(rows),2)
    budget.reserve_budget(rows,'1.8916352')
    with self.assertRaises(ValueError):budget.reserve_budget(rows,'1.8916353')
 def test_unapproved_restart_blocked(self):
  with patch.object(study,'MANIFEST','study/nonexistent-restart-manifest.json'):
   with self.assertRaises(FileNotFoundError):study.verify_freeze()
 def test_stop_after_first_fault_no_retry(self):
  with tempfile.TemporaryDirectory() as d,patch.object(study,'RESULTS_ROOT',Path(d)),patch.object(budget,'RESULTS_ROOT',Path(d)),patch.object(study,'COHORT',Path(d)/'cohort.json'),patch.object(study,'verify_freeze',return_value={}),patch.object(study,'configure'),patch.object(study,'flow',side_effect=study.StudyStop('mock infrastructure fault')) as run:
   result=study.execute();self.assertEqual(run.call_count,1);self.assertEqual(result['status'],'STOPPED')
if __name__=='__main__':unittest.main()
