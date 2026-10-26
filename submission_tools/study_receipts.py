"""Run the unchanged Day6 pilot and wrap every new/changed result with provenance.
Standalone stdlib: copy outside the checkout before switching to day6.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
PIN='ef9d36b0e4cf546d45cae469fb61d5d69f27a80e'
def command(root,*args):return subprocess.check_output(['git',*args],cwd=root)
def verify(root):
 if command(root,'rev-parse','HEAD').decode().strip()!=PIN:raise ValueError('Study runtime must be exactly '+PIN)
 if command(root,'branch','--show-current').decode().strip()!='day6':raise ValueError('Study must run on day6')
 for name in command(root,'ls-tree','-r','--name-only',PIN).decode().splitlines():
  if name.startswith('results/'):continue
  path=root/name
  if path.is_symlink() or not path.is_file() or path.read_bytes()!=command(root,'show',PIN+':'+name):raise ValueError('Runtime drift: '+name)
 return PIN

def snapshot(root):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'results').glob('*.json')}
def capture(root,out,before):
 verify(root);out=Path(out)
 if out.exists():raise ValueError('Receipt output already exists')
 out.mkdir(parents=True)
 count=0
 for path in sorted((root/'results').glob('*.json')):
  raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if before.get(path.name)==sha:continue
  row={'runtime_commit':PIN,'runtime_branch':'day6','result_file':path.name,'original_sha256':sha,
       'record_kind':'provenance envelope; original result retained unchanged','result':json.loads(raw)}
  (out/path.name).write_text(json.dumps(row,indent=2)+'\n');count+=1
 (out/'RECEIPTS.json').write_text(json.dumps({'runtime_commit':PIN,'result_count':count,'original_results_modified':False},indent=2)+'\n')
 return count

def main():
 p=argparse.ArgumentParser();p.add_argument('--checkout',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--execute-pilot',action='store_true');p.add_argument('--verify-only',action='store_true');a=p.parse_args();root=a.checkout.resolve()
 verify(root)
 if a.verify_only:print('Verified exact Day6 runtime '+PIN);return
 if not a.execute_pilot:p.error('Choose --verify-only or --execute-pilot')
 from datetime import datetime
 from zoneinfo import ZoneInfo
 if datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()!='2026-10-27':raise ValueError('No paid calls today; pilot is scheduled for 2026-10-27')
 if a.out.resolve().is_relative_to(root) or a.out.exists():raise ValueError('Use a new receipt folder outside the checkout')
 before=snapshot(root)
 try:subprocess.run([sys.executable,'scripts/clean_pilot.py','--execute'],cwd=root,check=True)
 finally:print('Provenance envelopes saved:',capture(root,a.out,before))
if __name__=='__main__':
 try:main()
 except (ValueError,OSError,subprocess.CalledProcessError) as error:raise SystemExit(str(error))
