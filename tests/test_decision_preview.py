import copy,json,subprocess,tempfile,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from muse_guard.rules import actions
from muse_guard.quality_gate import input_space
from submission_tools.judge_demo import ASSETS,demo_tables
from tests.test_judge_demo import parity_cases

class DecisionPreviewTests(unittest.TestCase):
 def test_all_demo_editor_states_match_checker_for_every_input_and_choice(self):
  from submission_tools.decision_preview import preview
  for case in parity_cases():
   req=case['table'];before=copy.deepcopy(req);got=preview(req)
   self.assertEqual(got['checked'],len(input_space(req)))
   self.assertEqual(got['conflicts'],len(got['groups']))
   for group in got['groups']:
    variants=[]
    for choice in group['choices']:
     variant=copy.deepcopy(req);variant['rules']=[r for r in variant['rules'] if r.get('enabled',True)];variant['priority']=choice['priority'];variants.append(variant)
    expected=[{'input':x,'actions':[actions(v,x)[0] for v in variants]} for x in input_space(req) if actions(variants[0],x)!=actions(variants[1],x)]
    self.assertEqual(group['rows'],expected);self.assertEqual(group['affected_inputs'],len(expected))
   self.assertEqual(req,before)
 def test_grouping_replaces_duplicate_cards_and_same_actions_have_no_conflict(self):
  from submission_tools.decision_preview import preview,html_preview,cli_preview
  req=demo_tables()[0];got=preview(req)
  self.assertEqual(got['conflicts'],1);self.assertEqual(got['groups'][0]['affected_inputs'],2)
  for text in (html_preview(req),cli_preview(req)):
   self.assertIn('1 conflict (A vs B), 2 inputs affected',text)
   self.assertIn('A wins',text);self.assertIn('B wins',text)
  req['rules'][1]['action']=req['rules'][0]['action'];self.assertEqual(preview(req)['groups'],[])
 def test_javascript_preview_matches_python_on_all_144_states(self):
  from submission_tools.decision_preview import preview
  cases=parity_cases()
  script="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync(process.argv[1],'utf8'));const c=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(c.map(x=>MuseGuardClashes.preview(x.table))));"
  got=json.loads(subprocess.check_output(['node','-e',script,str(ASSETS/'clashes.js')],input=json.dumps(cases).encode()))
  self.assertEqual(got,[preview(c['table']) for c in cases])
 def test_continuous_cli_shows_preview_before_asking_and_never_implements_on_eof(self):
  from submission_tools.continuous import run
  root=Path(__file__).resolve().parents[1];doc=(root/'demo/continuous/refund.md').read_text();packet=json.loads((root/'demo/continuous/fake-response.json').read_text());output=StringIO()
  def ask(prompt):
   self.assertIn('A wins',output.getvalue());self.assertIn('B wins',output.getvalue());raise EOFError
  with tempfile.TemporaryDirectory() as d,redirect_stdout(output),patch('builtins.input',side_effect=ask),patch('submission_tools.continuous.implement') as implement:
   with self.assertRaises(EOFError):run(doc,Path(d)/'run',fake_packet=packet,accept_all=True)
   implement.assert_not_called()
   page=(Path(d)/'run/index.html').read_text();self.assertIn('Decision preview',page);self.assertIn('1 conflict (A vs B), 1 input affected',page)
 def test_saved_run_view_adds_preview_without_changing_record(self):
  from submission_tools.presentation import render
  root=Path(__file__).resolve().parents[1];row=json.loads((root/'results/recovery-289db424fb09-view-day5.json').read_text());before=copy.deepcopy(row)
  page=render(row,static=True)
  self.assertIn('Decision preview',page);self.assertIn('1 conflict (A vs B), 2 inputs affected',page);self.assertEqual(row,before)

 def test_catalog_cli_display_hook_prints_before_original_choice_and_restores(self):
  from submission_tools.presentation import display_hooks
  from muse_guard import recovery,view
  original_choose=recovery.choose_decision;original_render=view.render;output=StringIO()
  with redirect_stdout(output),display_hooks('refund-impossible'):
   result=recovery.choose_decision(['A','B'],decide='B')
  self.assertEqual(result,('B','scripted developer CLI'));self.assertIn('1 conflict (A vs B), 2 inputs affected',output.getvalue())
  self.assertIn('\nInput -> A wins | B wins\n',output.getvalue())
  self.assertIs(recovery.choose_decision,original_choose);self.assertIs(view.render,original_render)
 def test_completion_claim_denominators_are_counted_from_original_phase_records(self):
  root=Path(__file__).resolve().parents[1];cohort=json.loads((root/'study_runs/holdout-third-2026-10-27/cohort.json').read_text())
  for mode,wanted in [('plain',[40,37]),('guarded',[37,40])]:
   counts=[]
   for phase in ('attempt','repair'):
    rows=[e['record'][phase] for e in cohort['entries'] if e['mode']==mode and phase in e['record']]
    self.assertEqual(len(rows),80 if phase=='attempt' else 40)
    counts.append(sum(r.get('completion_claim') is True for r in rows))
   self.assertEqual(counts,wanted);self.assertEqual(sum(counts),77)
  for name in ('README.md','docs/MEASURED_RESULTS.md'):
   self.assertIn('0/77',(root/name).read_text())
