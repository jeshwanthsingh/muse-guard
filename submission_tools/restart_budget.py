"""One executor ledger: daily rehearsals or all prior study cohorts, never both."""
import json,subprocess
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
RESULTS_ROOT=ROOT/'study_runs/third-holdout-2026-10-27'
CAP=Decimal('70')
KIND='study'
TOTAL=ROOT/'study_runs/study-total.json'
PRIOR_ROOTS=[ROOT/'study_runs/holdout-2026-10-27',ROOT/'study_runs/holdout-restart-2026-10-27']
def inside(path):
 p=Path(path).resolve()
 if not p.is_relative_to(ROOT.resolve()):raise ValueError('Output outside repository: '+str(path))
 return p
def validate_root():
 if ROOT.name!='muse-guard' or not (ROOT/'.git').exists() or not all((ROOT/n).is_file() for n in ('muse_guard/runner.py','submission_tools/restart_budget.py','study/HOLDOUT_ALLOCATION-2026-10-27.json')):raise ValueError('Invalid muse-guard repository root')
 actual=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip()).resolve()
 if actual!=ROOT.resolve():raise ValueError('ROOT differs from Git root')
def configure(plan):
 global RESULTS_ROOT,CAP,KIND,TOTAL
 validate_root();KIND=plan['budget'];CAP=Decimal('5' if KIND=='daily' else '70')
 RESULTS_ROOT=inside(ROOT/plan['output']);TOTAL=inside(ROOT/('results/total.json' if KIND=='daily' else 'study_runs/study-total.json'))
 if KIND not in ('daily','study'):raise ValueError('Unknown budget')
 for p in (RESULTS_ROOT,RESULTS_ROOT/'raw',RESULTS_ROOT/'progress.log',RESULTS_ROOT/'cohort.json',TOTAL):inside(p)
 # Reject existing symlinks anywhere under output (including dangling links).
 if RESULTS_ROOT.exists() and any(p.is_symlink() for p in RESULTS_ROOT.rglob('*')):raise ValueError('Output contains symlink')
def ledger_records(results,day=None):
 if inside(results)!=RESULTS_ROOT.resolve():raise ValueError('Wrong ledger output')
 if KIND=='daily':
  dirs=[ROOT/'results']+list((ROOT/'results').glob('rehearsal-*'))
 else:dirs=PRIOR_ROOTS+[RESULTS_ROOT]
 seen=set();rows=[];today=datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
 for directory in dict.fromkeys(dirs):
  inside(directory)
  for p in directory.glob('*.json'):
   r=json.loads(p.read_text())
   if not isinstance(r,dict):raise ValueError('Non-object ledger artifact')
   if 'run_id' not in r or (KIND=='daily' and r.get('date')!=today):continue
   if r['run_id'] in seen:raise ValueError('Duplicate phase receipt')
   seen.add(r['run_id']);rows.append(r)
 return rows

def cost_sum(rows):
 values=[]
 for r in rows:
  if r.get('cost_usd') is None:raise ValueError('Unknown usage; STOP')
  v=Decimal(str(r['cost_usd']))
  if not v.is_finite() or v<0:raise ValueError('Invalid receipt cost')
  values.append(v)
 return sum(values,Decimal(0))
def reserve_budget(records,reservation):
 amount=Decimal(str(reservation))
 if not amount.is_finite() or amount<=0 or cost_sum(records)+amount>CAP:raise ValueError('Budget reservation exceeds cap')
 return reservation

def self_check():
 validate_root()
 for p in (RESULTS_ROOT,TOTAL,*PRIOR_ROOTS):inside(p)
 expected=cost_sum(ledger_records(RESULTS_ROOT))
 if not TOTAL.is_file():raise ValueError('Running budget total missing')
 actual=Decimal(str(json.loads(TOTAL.read_text())['known_cost_usd']))
 if abs(actual-expected)>Decimal('0.000000001'):raise ValueError('Running budget total differs from all prior receipts')
 return {'root_verified':True,'outputs_inside_repo':True,'prior_receipts_usd':float(expected),'running_total_usd':float(actual),'cap_usd':float(CAP)}
def save_total(results,day=None):
 rows=ledger_records(results);known=sum((Decimal(str(r['cost_usd'])) for r in rows if r.get('cost_usd') is not None),Decimal(0));unknown=any(r.get('cost_usd') is None for r in rows)
 report={'budget':KIND,'limit_usd':float(CAP),'known_cost_usd':float(known),'unknown_usage':unknown,'run_count':len(rows),'can_start':not unknown and known<CAP}
 if KIND=='daily':report['date']=datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
 for p in (TOTAL,Path(results)/'total.json'):
  inside(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n')
 return report
