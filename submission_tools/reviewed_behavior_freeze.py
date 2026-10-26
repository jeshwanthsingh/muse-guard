"""Prepare a supplemental freeze after the exact Day6 pilot; never run a model."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from submission_tools.behavior_score import amended_summary,POLICY
from submission_tools.study_receipts import PIN
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def prepare(pilot_root,out,reviewed=False):
 root=Path(pilot_root).resolve();out=Path(out)
 if not reviewed:raise ValueError('Review the completed pilot before using --reviewed')
 if out.exists():raise ValueError('Never overwrite an existing supplemental freeze')
 code='''import json
from muse_guard.pilot import load_entries,freeze_ready,source_hashes
from pathlib import Path
p=Path("results/CLEAN_PILOT_2026-10-27.json")
c,e=load_entries(p)
if c.get("status")!="FINISHED" or not freeze_ready(e):raise ValueError("Incomplete, unaccounted or invalid pilot")
print(json.dumps({"cohort":c,"entries":e}))
'''
 try:data=json.loads(subprocess.check_output([sys.executable,'-c',code],cwd=root))
 except subprocess.CalledProcessError:raise ValueError('Pilot evidence did not validate; no freeze created') from None
 if data['cohort'].get('source_revision')!=PIN:raise ValueError('Pilot was not run at the approved Day6 commit')
 paths=[POLICY,'submission_tools/behavior_score.py','submission_tools/reviewed_behavior_freeze.py']
 evaluator={name:sha(ROOT/name) for name in paths}
 # No uncommitted scoring policy may be described as a reviewed freeze.
 for name,wanted in evaluator.items():
  raw=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
  if hashlib.sha256(raw).hexdigest()!=wanted:raise ValueError('Commit the approved policy/scorer before freezing')
 pilot=root/'results/CLEAN_PILOT_2026-10-27.json'
 parents={name:sha(root/name) for name in ('datasets/holdout/MANIFEST.json','study/MANIFEST-day4.json')}
 from muse_guard.freeze import LOCKED_FILES
 tree=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PIN],cwd=root,text=True).splitlines())
 if set(data['cohort']['source_hashes'])!=set(LOCKED_FILES)&tree:raise ValueError('Day6 source inventory incomplete')
 for name,wanted in parents.items():
  original=subprocess.check_output(['git','show',PIN+':'+name],cwd=root)
  if hashlib.sha256(original).hexdigest()!=wanted:raise ValueError('Parent manifest drift')
 for name,wanted in data['cohort']['source_hashes'].items():
  original=subprocess.check_output(['git','show',PIN+':'+name],cwd=root)
  if hashlib.sha256(original).hexdigest()!=wanted:raise ValueError('Pilot did not use exact Day6 source')
 frozen=json.loads((root/'datasets/holdout/MANIFEST.json').read_text())
 if len(frozen.get('data_files',{}))!=20:raise ValueError('Expected 20 frozen holdout pairs')
 for name,wanted in frozen['data_files'].items():
  if sha(root/name)!=wanted:raise ValueError('Holdout data drift')
 report={'schema':'behavior-only-supplement-v1','kind':'reviewed supplemental freeze; not a replacement active runtime manifest',
  'runtime_commit':PIN,'pilot_sha256':sha(pilot),'runtime_source_hashes':data['cohort']['source_hashes'],
  'parent_manifests':parents,'holdout_data_hashes':frozen['data_files'],'scorer_files':evaluator,
  'scorer_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'review_declaration':'local --reviewed; not external identity proof','amended_pilot':amended_summary(data['entries']),
  'holdout_execution_authorized':False}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pilot-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--reviewed',action='store_true');a=p.parse_args()
 try:prepare(a.pilot_root,a.out,a.reviewed);print(a.out)
 except (ValueError,OSError) as error:p.exit(2,str(error)+'\n')
