"""Coverage and one-action clarification for historical pages; no evidence edits."""
import json
from pathlib import Path
from html import escape
from muse_guard.rules import build_task,digest,TASKS
from muse_guard.metrics import checker_inventory
ROOT=Path(__file__).resolve().parents[1]
def panel(identity):
 path=ROOT/'results'/(identity+'.json')
 if not path.is_file():return '<section class="panel"><h2>Boundary: planted fixture</h2><p>Synthetic fixture; not model performance. One next action per input. Original test edits are descriptive under the new recovery amendment; incorrect behavior still fails.</p><p>What this does NOT check: extraction accuracy, undeclared inputs or production systems.</p></section>'
 row=json.loads(path.read_text());phase=row.get('repair',row);req=row.get('requirements_v2',row.get('requirements_v1'))
 if not req:
  task=TASKS.get(row.get('task',''))
  if task and digest(task['requirements'])==phase.get('requirements_hash'):req=task['requirements']
 checked='Declared-input coverage unavailable; '+str(len(phase.get('tests',[])))+' historical check rows recorded.'
 if req and req.get('input_space'):
  task=build_task(req)
  values=task['visible_cases']+task['hidden_cases'];distinct={json.dumps(v,sort_keys=True) for v,a in values}
  import math
  declared=math.prod(len(v) for v in req['input_space'].values())
  hashes=(phase.get('visible_tests_hash')==digest(task['test_source']) and phase.get('hidden_tests_hash')==digest(task['hidden_test_source']))
  if hashes and checker_inventory(phase):checked=str(len(distinct))+' / '+str(declared)+' declared inputs checked in this historical record.'
  else:checked=str(declared)+' declared inputs; complete executed coverage is not verified from this extract.'
 pair=(req or {}).get('pair','')
 meanings=('Choose ONE next action: refund means refund immediately; manual_review means do not refund until manual review.' if pair=='refund' else
           'Choose ONE next action: retry means retry this request now; stop means do not retry this request.' if pair=='retry' else 'Choose ONE next action for each input.')
 return '<section class="panel"><h2>Coverage and action meanings</h2><p>'+escape(checked)+'</p><p>'+escape(meanings)+'</p><p>Original recorded rule wording and scores are retained. This clarification does not rescore history.</p><p>Rejected / unconverted source sentences: not applicable; these historical tasks used authored rules.</p><p>What this does NOT check: English extraction accuracy, omitted requirements, undeclared inputs or real-world system behavior.</p></section>'
