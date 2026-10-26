"""Compare worktree AND index to the approved submission base. No model calls."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='03b558b5259a6ec706d6a12cb7dd24a16942f434'
def git(*args,root=ROOT):return subprocess.check_output(['git',*args],cwd=root)
def verify(root=ROOT):
 root=Path(root);manifest=json.loads((root/'submission_tools/protected.json').read_text());errors=[]
 if manifest['base_commit']!=BASE:raise ValueError('Protected baseline anchor changed')
 # Derive expected hashes from immutable Git objects, not mutable manifest values.
 for name,wanted in manifest['files'].items():
  original=hashlib.sha256(git('show',BASE+':'+name,root=root)).hexdigest()
  if wanted!=original:errors.append(name+' baseline')
  path=root/name
  if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=original:errors.append(name+' worktree')
  try:
   if hashlib.sha256(git('show',':'+name,root=root)).hexdigest()!=original:errors.append(name+' staged')
  except subprocess.CalledProcessError:errors.append(name+' missing staged file')
 # Coverage is anchored by the original evidence plus the original spec manifest.
 baseline=json.loads(git('show',BASE+':results/SPEC_VERIFICATION.json',root=root))['protected_baseline_sha256']
 spec=json.loads(git('show',BASE+':spec_eval/MANIFEST.json',root=root))['files']
 expected=set(baseline)|set(spec)|{'spec_eval/MANIFEST.json'}
 if set(manifest['files'])!=expected:errors.append('manifest coverage')
 patterns=['muse_guard/*.py','muse_guard/*.json','muse_guard/view_assets/*','scripts/*.py','datasets/dev/*.json','datasets/holdout/*.json']
 staged=git('ls-files',root=root).decode().splitlines()
 import fnmatch
 for pattern in patterns:
  actual={str(p.relative_to(root)) for p in root.glob(pattern)}|{p for p in staged if fnmatch.fnmatchcase(p,pattern)}
  if actual-{p for p in expected if fnmatch.fnmatchcase(p,pattern)}:errors.append('protected inventory '+pattern)
 if errors:raise ValueError('Protected drift: '+', '.join(errors))
 return {'protected_files':len(expected),'base_commit':BASE,'status':'UNCHANGED'}
if __name__=='__main__':
 try:print(json.dumps(verify()))
 except (ValueError,OSError,subprocess.CalledProcessError) as error:raise SystemExit(str(error))
