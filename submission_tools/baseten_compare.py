"""DEV-only exploratory plan and offline preflight. Live execution remains disabled pending a validated token counter."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from submission_tools.baseten import MODEL,configuration
from muse_guard.rules import PAIRS
ROOT=Path(__file__).resolve().parents[1]
def plan():
 pairs=sorted(k for k,v in PAIRS.items() if v['split']=='dev')
 if len(pairs)!=10:raise ValueError('Expected ten development pairs')
 return {'kind':'exploratory DEV comparison; not frozen study','models':[MODEL,'muse-spark-1.3'],'repeat':1,
         'entries':[{'pair':p,'task':p+'-'+t,'backend':b,'decision':'B','mode':'guarded'} for p in pairs for t in ('solvable','impossible') for b in ('standard','baseten')],
         'daily_cap_usd':5,'holdout_calls':0,'live_status':'BLOCKED: validated Baseten pre-inference token counter and reviewed executor required'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--plan',action='store_true');p.add_argument('--preflight',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
 if a.plan:print(json.dumps(plan(),indent=2))
 elif a.preflight or a.execute:
  try:configuration()
  except ValueError as error:print(json.dumps({'status':'refused','reason':str(error),'live_status':plan()['live_status']}));raise SystemExit(2)
  print(json.dumps({'model':MODEL,'credentials_present':True,'endpoint_valid':True,'status':plan()['live_status']}))
  raise SystemExit(2)
 else:p.error('Choose --plan or --preflight')
