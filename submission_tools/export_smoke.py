"""Exactly two authorized DEV flows; no holdout execution capability."""
import argparse,fcntl,json,os,time,uuid,hashlib,subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from muse_guard.rules import TASKS,approve,build_task,verify_conflict
from muse_guard.quality_gate import accept_task
from muse_guard.recovery import frozen_solution
from submission_tools.behavior_score import score
from submission_tools.holdout_study import StudyStop,write,verify_freeze
from submission_tools.export_policy import phase_failure
from submission_tools.export_runtime.ledger import RESULTS_ROOT,ledger_records,save_total,reserve_budget
ROOT=Path(__file__).resolve().parents[1]
REPORT=RESULTS_ROOT/'EXPORT_SMOKE_2026-10-27.json'
def flow(entry,progress):
 from submission_tools.export_runtime.runner import run_one
 from submission_tools.export_runtime.card import conflict_card
 task=TASKS[entry['task']];mode=entry['mode'];start=time.monotonic()
 r={'recovery_id':'study-flow-'+uuid.uuid4().hex[:12],'date':datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat(),
    'task':entry['task'],'mode':mode,'repeat':entry['repeat'],'study_holdout':False,'status':'STARTED','requirements_v1':task['requirements'],'phase_run_ids':[]}
 path=RESULTS_ROOT/(r['recovery_id']+'.json');entry['record']=r;write(path,r);progress()
 def phase(name,row):
  r[name]=row;r['phase_run_ids'].append(row['run_id']);write(path,r);progress()
  error=phase_failure(row,RESULTS_ROOT,name=='conflict_card')
  if error:raise StudyStop(name+': '+error)
  return row
 try:
  a=phase('attempt',run_one(task,RESULTS_ROOT,mode=mode,allow_holdout=False,retain_session=mode=='plain',dollar_quota=True))
  if mode=='guarded':
   if a['outcome']!='CONFLICT VERIFIED':r['status']=a['outcome'];return
   report=a['conflict_report'];proof=verify_conflict(task['requirements'],report)
   phase('conflict_card',conflict_card(task['requirements'],proof,RESULTS_ROOT,dict(os.environ),dollar_quota=True))
  else:
   if a.get('conflict_report',{}).get('conflict') is not True:r['status']=a['outcome'];return
   admission=accept_task(task)
   report={'conflict':True,'rules':[v['id'] for v in task['requirements']['rules']],'witness':admission['witness'],'explanation':'Private author witness for common final scoring'}
  v2=approve(task['requirements'],'B',report,confirmed=True,source='scripted developer CLI')
  r.update(requirements_v2=v2,decision=v2['approval']['decision'])
  kwargs={'continuation':a} if mode=='plain' else {'seed_solution':frozen_solution(RESULTS_ROOT,a)}
  b=phase('repair',run_one(build_task(v2),RESULTS_ROOT,mode=mode,allow_holdout=False,dollar_quota=True,**kwargs))
  judged=score(b,v2)
  if not judged['evidence_complete']:raise StudyStop('approved-v2 scoring evidence incomplete')
  r['status']='RECOVERED' if judged['recovered'] else 'RECHECK DID NOT PASS'
 except StudyStop as error:r.update(status='STOPPED',stop_reason=str(error));raise
 finally:
  phases=[r[n] for n in ('attempt','repair','conflict_card') if n in r]
  r['cost_usd']=sum(x['cost_usd'] for x in phases) if all(x.get('cost_usd') is not None for x in phases) else None
  r['time_seconds']=round(time.monotonic()-start,3);write(path,r);progress()

def execute():
    verify_freeze()
    if REPORT.exists():raise ValueError('Smoke already started; no retry')
    entries=[{'task':'refund-impossible','kind':'impossible','mode':m,'repeat':1,'record':None} for m in ('plain','guarded')]
    files=list((ROOT/'submission_tools/export_runtime').glob('*.py'))+[Path(__file__),ROOT/'submission_tools/export_policy.py']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    report={'status':'STARTED','entries':entries,'source_hashes':hashes,'holdout_calls':0}
    with (RESULTS_ROOT/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        write(REPORT,report)
        try:
            for e in entries:
                for name,h in hashes.items():
                    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise StudyStop('Source drift')
                reserve_budget(ledger_records(RESULTS_ROOT,datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()),'2.788')
                print('START '+e['mode'],flush=True)
                flow(e,lambda:write(REPORT,report))
                print('END '+e['mode']+' '+e['record']['status'],flush=True)
            report['status']='COMPLETE'
        except (StudyStop,ValueError,OSError,KeyError,TypeError,KeyboardInterrupt) as error:
            report.update(status='STOPPED',stop_reason=str(error))
        finally:write(REPORT,report)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');args=p.parse_args()
    if not args.execute:p.error('Choose --execute (DEV only)')
    print(json.dumps(execute(),indent=2))
