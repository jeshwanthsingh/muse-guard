"""Complete only the unstarted guarded dev flow after a non-ledger artifact error.
Never rerun the plain attempt/repair; recover their saved immutable phase receipt.
"""
import json,fcntl,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from submission_tools import export_smoke as smoke
from submission_tools.export_policy import phase_failure
from submission_tools.behavior_score import score
from submission_tools.holdout_study import write

def execute():
 with (smoke.RESULTS_ROOT/'.run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  c=json.loads(smoke.REPORT.read_text())
  if c['status']!='STARTED' or c['entries'][1]['record'] is not None:raise ValueError('Unstarted guarded flow required; no retry')
  for name,h in c['source_hashes'].items():
   if hashlib.sha256((smoke.ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('Smoke runtime drift')
  r=c['entries'][0]['record']
  if r['attempt']['run_id']!='refund-impossible-v1-25f267ba434e' or 'repair' in r:raise ValueError('Unexpected original smoke')
  repair=json.loads((smoke.RESULTS_ROOT/'refund-impossible-v2-ede5df72d03a.json').read_text())
  if repair['session_id']!=r['attempt']['session_id'] or phase_failure(repair,smoke.RESULTS_ROOT):raise ValueError('Saved repair incomplete')
  if not score(repair,r['requirements_v2'])['recovered']:raise ValueError('Saved repair did not recover')
  r['repair']=repair;r['phase_run_ids'].append(repair['run_id']);r['status']='RECOVERED'
  r['cost_usd']=r['attempt']['cost_usd']+repair['cost_usd'];r['reconstructed_from_saved_phase']=True
  c['bookkeeping_incident']='Diagnostic list temporarily placed in daily ledger directory; removed. Plain repair completed; wrapper reconstructed from saved receipt. No model retry.'
  write(smoke.RESULTS_ROOT/(r['recovery_id']+'.json'),r);write(smoke.REPORT,c)
  try:
   smoke.reserve_budget(smoke.ledger_records(smoke.RESULTS_ROOT,datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()),'2.788')
   print('START guarded only; plain not rerun',flush=True)
   smoke.flow(c['entries'][1],lambda:write(smoke.REPORT,c))
   c['status']='COMPLETE'
  except (smoke.StudyStop,ValueError,OSError,KeyError,TypeError,KeyboardInterrupt) as error:c.update(status='STOPPED',stop_reason=str(error))
  finally:write(smoke.REPORT,c)
  return c
if __name__=='__main__':print(json.dumps(execute(),indent=2))
