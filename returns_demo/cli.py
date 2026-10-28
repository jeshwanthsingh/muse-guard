"""One service recovery command; real mode always requires interactive review."""
import argparse
import json
from pathlib import Path
from returns_demo.flow import run


def main(argv=None):
    parser=argparse.ArgumentParser(prog='muse-guard returns')
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--fake-response',type=Path);source.add_argument('--real',action='store_true')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        fake=json.loads(args.fake_response.read_text()) if args.fake_response else None
        row=run(args.out,fake_packet=fake)
        print(json.dumps({k:row.get(k) for k in ('status','outcome','cost_usd','paid_calls')}));print(args.out/'index.html')
        if row['status']!='CHECKED':parser.exit(2,'Stopped before a completed recheck; evidence retained.\n')
    except (EOFError,KeyboardInterrupt):parser.exit(130,'Stopped for human input; evidence retained, no implicit choice.\n')
    except (ValueError,OSError,KeyError,TypeError) as error:parser.exit(2,str(error)+'\n')


if __name__=='__main__':main()
