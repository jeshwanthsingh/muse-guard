"""Predeclared dev-only pilot. Holds the canonical lock; never resets spend."""
import fcntl,json,os,random,sys,time
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from muse_guard.rules import TASKS
from muse_guard.recovery import recover
from muse_guard.plain import recover_plain
from muse_guard.runner import save_total
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1];RESULTS=ROOT/'results'
plan=[];rng=random.Random(20261026)
for pair in ('retry','refund','shipping'):
 for twin in ('solvable','impossible'):
  modes=['plain','guarded'];rng.shuffle(modes)
  for mode in modes:plan.append({'task':pair+'-'+twin,'mode':mode})
for item in plan:assert TASKS[item['task']]['split']=='dev'
output=RESULTS/'DAY5_PILOT.json'
resume='--resume' in sys.argv
if output.exists() and not resume:raise SystemExit('Pilot already recorded; do not overwrite/repeat')
previous=json.loads(output.read_text()) if resume else None
if resume and previous.get('status')!='INTERRUPTED FOR ISOLATION FIX':raise SystemExit('Only the recorded interruption may resume')
record={'pilot_id':'day5-dev-pilot','date':datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat(),
        'study_results':False,'holdout_model_calls':0,'repeats':1,'order_seed':20261026,
        'plan':plan,'flows':[],'status':'RUNNING','quota_policy':'same per-request remaining-dollar hard cap in both modes'}
if previous:
 record=previous;record['status']='RESUMED WITH FIXED ISOLATION'
 record['resume_implementation_commit']=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
output.write_text(json.dumps(record,indent=2)+'\n')
with (RESULTS/'.run.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for item in plan[len(record['flows']):]:
  total=save_total(RESULTS,record['date'])
  if total['total_upper_bound_usd']>=5 or not total['can_start']:
   record['flows'].append(dict(item,status='NOT STARTED',reason='Daily cap or unresolved usage'))
  else:
   row=(recover_plain(RESULTS,task_name=item['task'],decision='B',dollar_quota=True) if item['mode']=='plain' else
        recover(RESULTS,'B',task_name=item['task'],dollar_quota=True))
   record['flows'].append(dict(item,record_id=row['recovery_id'],status=row['status'],cost_usd=row.get('cost_usd'),phase_run_ids=row['phase_run_ids'],harness_version='fixed-isolation' if previous else 'pre-isolation-fix'))
   print(json.dumps(record['flows'][-1]),flush=True)
  output.write_text(json.dumps(record,indent=2)+'\n')
 record['status']='FINISHED';record['total']=save_total(RESULTS,record['date'])
 record['actual_cost_usd']=float(sum((Decimal(str(f['cost_usd'])) for f in record['flows'] if f.get('cost_usd') is not None),Decimal(0)))
 output.write_text(json.dumps(record,indent=2)+'\n')
print('PILOT COMPLETE',record['actual_cost_usd'],record['total']['total_upper_bound_usd'],flush=True)
