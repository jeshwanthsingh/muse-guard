"""Planted local Git fixtures for the future reviewed manifest. No real freeze/model."""
import json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from muse_guard.freeze import sha,verify_freeze

class ReviewedFreezeTests(unittest.TestCase):
 def test_new_manifest_retains_both_parents_and_pins_pilot(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);folder=root/'datasets/holdout';folder.mkdir(parents=True);(root/'study').mkdir();(root/'results').mkdir()
   prompt=root/'prompt';prompt.write_text('preregistered fixture')
   data={}
   for i in range(20):
    path=folder/('h%02d.json'%i);path.write_text('{}');data[str(path.relative_to(root))]=sha(path)
   old=folder/'MANIFEST.json';old.write_text(json.dumps({'schema_version':1,'holdout_pair_count':20,'data_files':data,'protocol_files':{'prompt':sha(prompt)}}))
   env={'PATH':os.environ['PATH'],'HOME':directory,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_NOSYSTEM':'1'}
   def git(*args):return subprocess.check_output(['git',*args],cwd=root,env=env,stderr=subprocess.DEVNULL)
   def commit(message):git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-m',message)
   git('init','-b','main');commit('original')
   parent=root/'study/MANIFEST-day4.json';parent.write_text('{}');commit('parent')
   active='study/MANIFEST-clean-2026-10-27.json'
   (root/'study/protocol.json').write_text(json.dumps({'active_manifest':active}))
   pilot=root/'results/pilot.json';cohort={'source_hashes':{'prompt':sha(prompt)}};pilot.write_text(json.dumps(cohort))
   manifest={'schema_version':3,'holdout_pair_count':20,'data_files':data,'protocol_files':cohort['source_hashes'],
     'parent_manifests':{'datasets/holdout/MANIFEST.json':sha(old),'study/MANIFEST-day4.json':sha(parent)},
     'pilot_record':'results/pilot.json','pilot_sha256':sha(pilot)}
   (root/active).write_text(json.dumps(manifest));commit('reviewed fixture')
   with patch('muse_guard.freeze.ROOT',root),patch('muse_guard.freeze.LOCKED_FILES',('prompt',)),patch('muse_guard.pilot.load_entries',return_value=(cohort,[])):
    self.assertEqual(verify_freeze()['manifest'],active)
    pilot.write_text('{}')
    with self.assertRaisesRegex(ValueError,'drift'):verify_freeze()
    pilot.write_text(json.dumps(cohort));parent.write_text('{"changed":true}')
    with self.assertRaisesRegex(ValueError,'original commit'):verify_freeze()
 def test_cohort_load_rejects_modified_phase_record(self):
  from muse_guard.pilot import load_entries
  plan=json.loads((Path(__file__).resolve().parents[1]/'study/clean_pilot_plan.json').read_text())
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'study').mkdir();(root/'results').mkdir()
   p=root/'study/plan.json';p.write_text(json.dumps(plan))
   phase=root/'results/phase.json';row={'run_id':'phase','cost_usd':0};phase.write_text(json.dumps(row))
   rec=root/'results/record.json';rec.write_text(json.dumps({'attempt':row}))
   entries=[dict(e,record_id=None) for e in plan['entries']]
   entries[0].update(record_id='record',record_sha256=sha(rec),phase_sha256={'phase':sha(phase)})
   cohort=root/'results/pilot.json';cohort.write_text(json.dumps({'schema':1,'plan_sha256':sha(p),'entries':entries}))
   with patch('muse_guard.pilot.ROOT',root),patch('muse_guard.pilot.PLAN',p):
    self.assertEqual(load_entries(cohort)[1][0]['record']['attempt'],row)
    phase.write_text('{}')
    with self.assertRaisesRegex(ValueError,'Phase evidence changed'):load_entries(cohort)
