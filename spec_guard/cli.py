"""Opt-in CLI wrapper; original commands retain the original executable path."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import uuid
from .core import review
from .provider import MODEL,propose
from .view import save

ROOT=Path(__file__).resolve().parents[1]


def decision(item,*,accept_all=False):
    row=item['proposal'];condition=row.get('when','otherwise')
    print('\nSOURCE: '+row['quote'])
    print('RULE:   '+json.dumps(condition,ensure_ascii=False)+' -> '+row['action'])
    if accept_all:
        print('DECISION: confirmed via --accept-all');return True
    while True:
        answer=input('Confirm this translation? [y/n] ').strip().lower()
        if answer in ('y','yes'):return True
        if answer in ('n','no'):return False
        print('Enter y to confirm or n to reject.')


def spec(args):
    path=args.document
    if path.is_symlink() or not path.is_file() or path.stat().st_size>16384:raise ValueError('Choose a UTF-8 requirements file <=16 KiB')
    doc=path.read_text()
    if not doc.strip():raise ValueError('Requirements document is empty')
    out=args.out or ROOT/'spec_runs'/('spec-'+uuid.uuid4().hex[:12])
    if out.exists():raise ValueError('Output already exists; no call was made')
    if args.response:
        packet=json.loads(args.response.read_text())
        if packet.get('kind')!='fake Spark response; constructed fixture, not observed model output':raise ValueError('Fake response must be explicitly labeled')
        proposal=packet['proposal'];cost={'model_invoked':False,'cost_usd':0};kind='fake'
    else:proposal,cost=propose(doc);kind='real'
    record=review(doc,proposal,lambda item:decision(item,accept_all=args.accept_all),model=MODEL,response_kind=kind,cost=cost)
    for item,choice in zip(record['validation']['items'],record['decisions']):
        if not item['valid']:print("couldn't convert: "+json.dumps(item['proposal'],ensure_ascii=False)+' | '+'; '.join(item['errors']))
    for item in record['validation']['unconverted']:print("couldn't convert / context: "+str(item['quote'])+' | '+str(item['reason']))
    for clash in record['clashes']:print('VERIFIED CLASH: '+json.dumps(clash,ensure_ascii=False))
    save(record,out)
    print(str(out/'confirmed.yaml'));print(str(out/'index.html'))
    return record


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    custom=bool(argv and argv[0]=='run' and len(argv)>1 and (Path(argv[1]).is_file() or argv[1].endswith(('.yaml','.json'))))
    if not argv or (argv[0] not in ('spec','spec-eval') and not custom):
        os.execv(sys.executable,[sys.executable,str(ROOT/'muse-guard'),*argv])
    parser=argparse.ArgumentParser(prog='muse-guard (spec extension)');sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('spec');p.add_argument('document',type=Path);source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--response',type=Path,help='Explicitly labeled fake Spark response; no paid call');source.add_argument('--real',action='store_true')
    p.add_argument('--accept-all',action='store_true');p.add_argument('--out',type=Path)
    p=sub.add_parser('spec-eval');p.add_argument('--real',action='store_true');p.add_argument('--fake',action='store_true');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('run');p.add_argument('rules',type=Path);source=p.add_mutually_exclusive_group()
    source.add_argument('--candidate',type=Path);source.add_argument('--real',action='store_true');p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='spec':spec(args)
        elif args.command=='spec-eval':
            from .evaluation import evaluate
            if args.real==args.fake:raise ValueError('Choose exactly --real or --fake')
            print(json.dumps(evaluate(args.out,real=args.real),indent=2))
        else:
            from .run import run_confirmed
            print(json.dumps(run_confirmed(args.rules,candidate=args.candidate,real=args.real,out=args.out),indent=2))
    except (ValueError,OSError,KeyError,TypeError,EOFError) as error:parser.error(str(error))
