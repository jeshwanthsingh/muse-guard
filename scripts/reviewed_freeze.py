"""Prepare the reviewed post-pilot manifest, never run a model or change holdouts."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from muse_guard.pilot import PLAN,ROOT,load_entries,freeze_ready,source_hashes,validate_day,sha
from muse_guard.freeze import LOCKED_FILES,committed_manifest,check_hashes
p=argparse.ArgumentParser();p.add_argument('--pilot',type=Path,required=True);p.add_argument('--reviewed',action='store_true')
a=p.parse_args()
try:
 plan=json.loads(PLAN.read_text());validate_day(plan)
 if not a.reviewed:raise ValueError('Review the complete pilot evidence before declaring --reviewed')
 cohort,entries=load_entries(a.pilot)
 if cohort.get('status')!='FINISHED' or not freeze_ready(entries):raise ValueError('Clean pilot is incomplete, unaccounted or has harness/budget failures')
 if cohort['source_hashes']!=source_hashes():raise ValueError('Runtime changed since the clean pilot; do not freeze it as tested')
 original,_,_=committed_manifest('datasets/holdout/MANIFEST.json');check_hashes(ROOT,original['data_files'])
 from muse_guard.rules import PAIRS
 from muse_guard.quality_gate import validate_pair
 gates=[validate_pair(pair) for pair in PAIRS.values() if pair['split']=='holdout']
 parents={}
 for name in ('datasets/holdout/MANIFEST.json','study/MANIFEST-day4.json'):
  committed_manifest(name);parents[name]=sha(ROOT/name)
 target=ROOT/json.loads((ROOT/'study/protocol.json').read_text())['active_manifest']
 if target.exists():raise ValueError('Never overwrite an existing freeze')
 manifest={'schema_version':3,'reviewed_on':plan['scheduled_date'],'review_declaration':'local CLI --reviewed; trusted host declaration, not external identity proof',
  'pilot_record':str(a.pilot.resolve().relative_to(ROOT)),'pilot_sha256':sha(a.pilot),'primary_measures':'docs/PRIMARY_MEASURES.md',
  'parent_manifests':parents,'holdout_pair_count':20,'holdout_task_count':40,'model_calls_on_holdouts_at_freeze':0,
  'data_files':original['data_files'],'protocol_files':source_hashes(),'quality_gate':gates}
 target.write_text(json.dumps(manifest,indent=2)+'\n');print(str(target.relative_to(ROOT)),sha(target))
except (ValueError,OSError,KeyError) as error:p.exit(2,str(error)+'\n')
