import argparse,json,os,sys
from pathlib import Path
from submission_tools.continuous import run
ROOT=Path(__file__).resolve().parents[1]
def main():
 args=sys.argv[1:]
 if not args or args[0]!='spec':os.execv(str(ROOT/'spec_guard/bin/muse-guard'),[str(ROOT/'spec_guard/bin/muse-guard'),*args])
 p=argparse.ArgumentParser(prog='muse-guard spec');p.add_argument('document',type=Path)
 source=p.add_mutually_exclusive_group(required=True);source.add_argument('--fake-response',type=Path);source.add_argument('--real',action='store_true')
 p.add_argument('--accept-all',action='store_true');p.add_argument('--decide');p.add_argument('--out',type=Path,required=True)
 a=p.parse_args(args[1:])
 try:
  if a.document.is_symlink() or a.document.stat().st_size>16384:raise ValueError('Invalid requirements file')
  packet=json.loads(a.fake_response.read_text()) if a.fake_response else None
  record=run(a.document.read_text(),a.out,fake_packet=packet,accept_all=a.accept_all,choice=a.decide)
  print(json.dumps({k:record.get(k) for k in ('status','outcome','declared_input_count','checked_input_count','cost_usd')}));print(a.out/'index.html')
 except (ValueError,OSError,KeyError,EOFError) as error:p.exit(2,str(error)+'\n')
