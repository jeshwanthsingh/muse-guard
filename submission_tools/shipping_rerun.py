"""One authorized corrected DEV flow; preserve the original cohort and scores."""
import argparse,fcntl,hashlib,json,os,subprocess,re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from muse_guard import runner
from muse_guard.plain import recover_plain
from muse_guard.pilot import load_entries,freeze_ready
from submission_tools.settlement import ReconciledGateway
from submission_tools.check_protected import verify as protected
from submission_tools.behavior_score import amended_summary
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'results/OCT27_SHIPPING_CORRECTION.json'
PATCHES=['submission_tools/settlement.py','submission_tools/shipping_rerun.py','docs/amendments/2026-10-27-known-usage-settlement.md']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def committed_files():
 out={}
 for name in PATCHES:
  raw=(ROOT/name).read_bytes()
  if subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)!=raw:raise ValueError('Commit correction before paid rerun')
  out[name]=hashlib.sha256(raw).hexdigest()
 return out

def execute():
 if datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()!='2026-10-27':raise ValueError('Authorized date is Oct27')
 if REPORT.exists():raise ValueError('One rerun only; evidence already exists')
 protected();sources=committed_files()
 original=ROOT/'results/CLEAN_PILOT_2026-10-27.json'
 c,entries=load_entries(original)
 target=next(e for e in entries if e['task']=='shipping-impossible' and e['mode']=='plain')
 if target['record']['repair']['run_id']!='shipping-impossible-v2-3c5f60d5f05a':raise ValueError('Unexpected original flow')
 report={'schema':1,'date':'2026-10-27','kind':'authorized single dev-flow corrective rerun','status':'STARTED',
  'original_pilot_sha256':sha(original),'original_record_id':target['record']['recovery_id'],
  'runtime_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'base_pilot_runtime_commit':c['source_revision'],'correction_files':sources,'original_results_overwritten':False,'holdout_calls':0}
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 with (ROOT/'results/.run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  old=runner.Gateway;runner.Gateway=ReconciledGateway
  try:
   record=recover_plain(ROOT/'results',task_name='shipping-impossible',decision='B',dollar_quota=True)
   report.update(status='FINISHED',record_id=record['recovery_id'],record_sha256=sha(ROOT/'results'/(record['recovery_id']+'.json')),
     phase_sha256={identity:sha(ROOT/'results'/(identity+'.json')) for identity in record['phase_run_ids']})
  finally:
   runner.Gateway=old;REPORT.write_text(json.dumps(report,indent=2)+'\n')
 return gate()

def gate():
 protected();c,entries=load_entries(ROOT/'results/CLEAN_PILOT_2026-10-27.json');r=json.loads(REPORT.read_text())
 if r['status']!='FINISHED' or r['original_pilot_sha256']!=sha(ROOT/'results/CLEAN_PILOT_2026-10-27.json'):raise ValueError('Correction evidence incomplete or original changed')
 if set(r['correction_files'])!=set(PATCHES):raise ValueError('Correction source inventory incomplete')
 if not re.fullmatch(r'[A-Za-z0-9_-]+',r['record_id']):raise ValueError('Invalid record identity')
 for name,wanted in r['correction_files'].items():
  raw=subprocess.check_output(['git','show',r['runtime_commit']+':'+name],cwd=ROOT)
  if hashlib.sha256(raw).hexdigest()!=wanted or sha(ROOT/name)!=wanted:raise ValueError('Correction source drift')
 record_path=ROOT/'results'/(r['record_id']+'.json')
 if sha(record_path)!=r['record_sha256']:raise ValueError('Corrective record drift')
 record=json.loads(record_path.read_text())
 if record['task']!='shipping-impossible' or record['mode']!='plain':raise ValueError('Wrong corrective assignment')
 for phase in ('attempt','repair'):
  value=record.get(phase)
  if value:
   p=ROOT/'results'/(value['run_id']+'.json')
   if sha(p)!=r['phase_sha256'].get(value['run_id']) or json.loads(p.read_text())!=value:raise ValueError('Phase drift')
 for item in entries:
  if item['task']=='shipping-impossible' and item['mode']=='plain':item['record']=record
 return {'original_gate_passes':False,'corrected_gate_passes':freeze_ready(entries),
   'interpretation':'Supplemental gate after one predeclared infrastructure correction; original cohort unchanged',
   'correction_sha256':sha(REPORT),'corrected_summary':amended_summary(entries),'study_authorized':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--gate',action='store_true');a=p.parse_args()
 if a.execute==a.gate:p.error('Choose --execute or --gate')
 print(json.dumps(execute() if a.execute else gate(),indent=2))
