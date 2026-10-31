import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from returns_demo import provider
from returns_demo.cli import shown
from returns_demo.source import ROOT

class ReturnsDateGateTests(unittest.TestCase):
 def test_only_the_two_approved_dates_pass(self):
  for day,ok in (('2026-10-29',True),('2026-10-31',True),('2026-10-30',False),('2026-11-01',False)):
   with patch.object(provider,'today',return_value=day):
    if ok:provider.require_real_date()
    else:self.assertRaises(ValueError,provider.require_real_date)
 def test_1031_allows_exactly_one_run_even_after_a_failed_one(self):
  with tempfile.TemporaryDirectory() as d,patch.object(provider,'RESULTS',Path(d)),patch.object(provider,'today',return_value='2026-10-31'):
   provider.require_unused_date()
   (Path(d)/'returns-extract-x.json').write_text(json.dumps({'date':'2026-10-31','cost_usd':0}))
   self.assertRaises(ValueError,provider.require_unused_date)
 def test_1029_receipts_do_not_block_1031(self):
  with tempfile.TemporaryDirectory() as d,patch.object(provider,'RESULTS',Path(d)),patch.object(provider,'today',return_value='2026-10-31'):
   (Path(d)/'returns-extract-x.json').write_text(json.dumps({'date':'2026-10-29','cost_usd':0.1}))
   provider.require_unused_date()
 def test_printed_path_is_repo_relative_even_for_an_absolute_out(self):
  self.assertEqual(str(shown(Path('returns_runs/r/index.html'))),'returns_runs/r/index.html')
  self.assertEqual(str(shown(ROOT/'returns_runs/r/index.html')),'returns_runs/r/index.html')
