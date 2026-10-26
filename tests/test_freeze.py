import tempfile
from pathlib import Path
import unittest
from muse_guard.freeze import check_hashes,sha

class FreezeTests(unittest.TestCase):
 def test_data_or_protocol_drift_is_refused(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);p=root/'prompt.txt';p.write_text('frozen prompt')
   expected={'prompt.txt':sha(p)};check_hashes(root,expected)
   p.write_text('changed prompt')
   with self.assertRaisesRegex(ValueError,'Frozen study drift'):check_hashes(root,expected)
 def test_symlink_or_missing_file_is_refused(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);p=root/'target';p.write_text('x');(root/'link').symlink_to(p)
   with self.assertRaises(ValueError):check_hashes(root,{'link':sha(p)})
   with self.assertRaises(ValueError):check_hashes(root,{'missing':sha(p)})

 def test_frozen_holdout_choice_cannot_change(self):
  from muse_guard.recovery import recover
  with self.assertRaisesRegex(ValueError,'scripted B'):
   recover('unused',decision='A',env={},task_name='unused',allow_holdout=True)

 def test_manifest_is_anchored_and_extra_json_is_rejected(self):
  import json,subprocess,os
  from unittest.mock import patch
  from muse_guard.freeze import verify_freeze
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);folder=root/'datasets/holdout';folder.mkdir(parents=True)
   (root/'prompt').write_text('fixed')
   data={}
   for i in range(20):
    p=folder/('h%02d.json'%i);p.write_text('{}');data[str(p.relative_to(root))]=sha(p)
   manifest={'schema_version':1,'holdout_pair_count':20,'data_files':data,'protocol_files':{'prompt':sha(root/'prompt')}}
   path=folder/'MANIFEST.json';path.write_text(json.dumps(manifest))
   env={'PATH':os.environ['PATH'],'HOME':directory,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_NOSYSTEM':'1'}
   def git(*args):subprocess.run(['git',*args],cwd=root,env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   git('init','-b','main');git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-m','freeze fixture')
   with patch('muse_guard.freeze.ROOT',root),patch('muse_guard.freeze.LOCKED_FILES',('prompt',)):
    self.assertEqual(verify_freeze()['pairs'],20)
    (folder/'z-extra.json').write_text('{}')
    with self.assertRaisesRegex(ValueError,'inventory changed'):verify_freeze()
    (folder/'z-extra.json').unlink()
    manifest['protocol_files']['prompt']='0'*64;path.write_text(json.dumps(manifest))
    with self.assertRaisesRegex(ValueError,'original commit'):verify_freeze()
