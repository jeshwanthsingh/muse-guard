"""Display-only fixtures; planted text/observations are explicitly synthetic."""
import copy,json,unittest
from pathlib import Path
from muse_guard.view import render
ROOT=Path(__file__).resolve().parents[1]

class Day5ViewTests(unittest.TestCase):
 def fixture(self):
  row=json.loads((ROOT/'results/recovery-289db424fb09.json').read_text())
  row['display_evidence']={'agent_message':'PLANTED DISPLAY FIXTURE: I cannot satisfy both rules.\nPlease choose a rule.',
   'behavior':[{'input':{'eligible':True,'fraud_hold':True,'context':'card'},'witness':True,'before':'Candidate failed','after':'manual_review'}]}
  return row
 def test_new_sections_selected_choice_and_actual_message_excerpt(self):
  row=self.fixture();before=copy.deepcopy(row);page=render(row,diff_text='-old\n+new')
  for value in ['Attempt','Conflict found','You decide','Repair','Checked','Muse Code stopped and asked','Refund policy','PLANTED DISPLAY FIXTURE: I cannot satisfy both rules.','Rules: v1 → approved v2','Behavior: before → after','Show code changes','Show full explanation']:
   self.assertIn(value,page)
  self.assertIn('aria-pressed="true"',page);self.assertIn('Selected',page)
  self.assertLess(page.index('Muse Code stopped and asked'),page.index('Task and rules'))
  self.assertEqual(row,before)
 def test_diff_has_no_added_blank_line_padding(self):
  page=render(self.fixture(),diff_text='-old\n+new')
  self.assertNotIn('display:block',page)
  self.assertIn('-old</span>\n<span class="add">+new',page)
 def test_no_fabricated_message_or_behavior_when_evidence_missing(self):
  row=self.fixture();row.pop('display_evidence')
  page=render(row)
  self.assertIn('Session message unavailable',page)
  self.assertIn('Behavior observations unavailable',page)
 def test_pending_and_failed_runs_do_not_claim_checked(self):
  row=self.fixture();row.pop('repair');row.pop('decision');row.pop('requirements_v2');row['status']='AWAITING DECISION'
  page=render(row)
  self.assertNotIn('class="step complete" data-stage="checked"',page)
  self.assertNotIn('Selected',page)

 def test_template_markers_in_agent_text_stay_literal_not_controls(self):
  row=self.fixture();row['display_evidence']['agent_message']='@@buttons@@ @@badge@@'
  page=render(row)
  self.assertIn('<blockquote>@@buttons@@ @@badge@@</blockquote>',page)
  self.assertEqual(page.count('data-winner='),2)
