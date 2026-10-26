"""One command for gated task recovery; no holdout model runs by default."""
import argparse
import fcntl
import json
from pathlib import Path
from .rules import PAIRS,TASKS
from .quality_gate import validate_pair
from .recovery import recover
from .runner import run_one

ROOT=Path(__file__).resolve().parents[1]


def evidence(row,results):
    final=row.get('repair',row.get('attempt',row))
    checks=final.get('tests',[])
    passed=sum(t['status']=='PASS' for t in checks)
    result=row.get('status',row.get('outcome','HARNESS ERROR'))
    name=row.get('recovery_id',row.get('run_id'))
    cost='unknown' if row.get('cost_usd') is None else f"${row['cost_usd']:.8f}"
    version=final.get('requirements_version',1)
    return f"{result} | requirements v{version} | checks {passed}/{len(checks)} | cost {cost} | record {results/(name+'.json')}"


def main():
    parser=argparse.ArgumentParser(prog='muse-guard')
    sub=parser.add_subparsers(dest='command',required=True)
    gate=sub.add_parser('gate');gate.add_argument('--split',choices=['dev','holdout','all'],default='dev')
    run=sub.add_parser('run');run.add_argument('task',choices=sorted(TASKS))
    run.add_argument('--decide',choices=['A','B']);run.add_argument('--plain',action='store_true')
    run.add_argument('--allow-holdout',action='store_true',help='Only for a separately authorized future frozen study')
    view=sub.add_parser('view');view.add_argument('record')
    view.add_argument('--live',action='store_true');view.add_argument('--port',type=int,default=0)
    view.add_argument('--no-open',action='store_true')
    args=parser.parse_args();results=ROOT/'results'
    if args.command=='view':
        from .view import serve
        path=Path(args.record).expanduser()
        if not path.exists():
            if Path(args.record).name!=args.record:parser.error('Record path does not exist')
            path=results/(args.record.removesuffix('.json')+'.json')
        try:serve(path,live=args.live,port=args.port,open_browser=not args.no_open)
        except (ValueError,OSError) as error:parser.error(str(error))
        return
    if args.command=='gate':
        for pair in PAIRS.values():
            if args.split=='all' or pair['split']==args.split:
                print(json.dumps(validate_pair(pair)),flush=True)
        return
    task=TASKS[args.task]
    validate_pair(PAIRS[task['pair']])
    if task.get('split')=='holdout':
        from .freeze import verify_freeze
        verify_freeze()
        if not args.allow_holdout:parser.error('No holdout model calls authorized; use only in a future approved study')
        if not args.plain and args.decide!='B':parser.error('Frozen guarded holdout policy requires --decide B')
    if args.plain and args.decide:parser.error('--decide applies only to recovery mode')
    results.mkdir(exist_ok=True)
    with (results/'.run.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        row=(run_one(task,results,mode='plain',allow_holdout=args.allow_holdout) if args.plain else
             recover(results,args.decide,task_name=args.task,allow_holdout=args.allow_holdout))
    print(evidence(row,results),flush=True)
