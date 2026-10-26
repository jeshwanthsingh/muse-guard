"""Display-only provenance-aware wording and safe inline-code fixtures."""
import json,unittest
from pathlib import Path
from muse_guard.view import render
ROOT=Path(__file__).resolve().parents[1]

class StoppedViewTests(unittest.TestCase):
 def fixture(self):
  row=json.loads((ROOT/'results/recovery-289db424fb09-view-day5.json').read_text())
  row['display_evidence']['agent_message']='I stopped: `solve()` cannot meet both rules. <script>bad</script>'
  return row
 def test_unchanged_starter_and_honest_report_get_stopped_label(self):
  page=render(self.fixture())
  self.assertIn('Not implemented (Muse stopped to ask)',page)
  self.assertNotIn('<td>Candidate failed</td>',page)
 def test_other_candidate_failure_keeps_failure_label(self):
  row=self.fixture();row['attempt']['frozen_sha256']['solution.py']='0'*64
  self.assertIn('<td>Candidate failed</td>',render(row))
 def test_backticks_become_safe_inline_code(self):
  page=render(self.fixture())
  self.assertIn('<code>solve()</code>',page);self.assertNotIn('<script>bad</script>',page)
  row=self.fixture();row['display_evidence']['agent_message']='`<img src=x onerror=bad>` @@buttons@@'
  page=render(row)
  self.assertIn('<code>&lt;img src=x onerror=bad&gt;</code>',page)
  self.assertEqual(page.count('data-winner='),2)
