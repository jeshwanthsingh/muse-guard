"""Offline Day4 limits and amendment lineage controls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

class Day4ProtocolTests(unittest.TestCase):
 def test_matched_limits_are_the_approved_values(self):
  import inspect
  from muse_guard.runner import run_one
  protocol=json.loads((ROOT/'study/protocol.json').read_text())
  self.assertEqual(protocol['max_model_steps'],12);self.assertEqual(protocol['max_tokens'],320000)
  self.assertEqual(protocol['timeout_seconds'],300)
  self.assertEqual(inspect.signature(run_one).parameters['max_model_steps'].default,12)
  self.assertEqual(inspect.signature(run_one).parameters['max_tokens'].default,320000)
  self.assertTrue(protocol['fair_plain_adapter_ready']);self.assertFalse(protocol['study_runs_authorized'])
 def test_new_reservation_refuses_before_model(self):
  from muse_guard.runner import run_one
  from muse_guard.rules import TASKS
  from datetime import datetime
  from zoneinfo import ZoneInfo
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);day=datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
   (root/'prior.json').write_text(json.dumps({'run_id':'prior','date':day,'cost_usd':3.7}))
   with patch('muse_guard.runner.Gateway',side_effect=AssertionError('Offline test must not contact provider')):
    row=run_one(TASKS['refund-solvable'],root,env={'META_API_KEY':'fixture'})
   self.assertFalse(row['model_invoked']);self.assertIn('$5',row['reason'])
 def test_initial_only_plain_is_explicitly_blocked_on_holdouts(self):
  from muse_guard.runner import run_one
  from muse_guard.rules import TASKS
  task=next(t for t in TASKS.values() if t['split']=='holdout')
  with tempfile.TemporaryDirectory() as directory,patch('muse_guard.freeze.verify_freeze',return_value={'protocol':'UNCHANGED'}):
   with patch('muse_guard.runner.Gateway',side_effect=AssertionError('Offline test must not contact provider')):
    row=run_one(task,directory,env={'META_API_KEY':'fixture'},mode='plain',allow_holdout=True)
   self.assertFalse(row['model_invoked']);self.assertIn('same-session',row['reason'])
 def test_amended_manifest_preserves_original_data_and_requires_parent(self):
  from muse_guard.freeze import check_amendment
  import hashlib
  old=b'{"original":true}'
  manifest={'schema_version':2,'parent_manifest_sha256':hashlib.sha256(old).hexdigest(),'data_files':{'holdout':'abc'}}
  original={'data_files':{'holdout':'abc'}}
  check_amendment(manifest,original,old)
  manifest['data_files']['holdout']='changed'
  with self.assertRaises(ValueError):check_amendment(manifest,original,old)
  manifest['data_files']=original['data_files'];manifest['parent_manifest_sha256']='0'*64
  with self.assertRaises(ValueError):check_amendment(manifest,original,old)

 def test_amended_freeze_is_anchored_and_detects_runtime_or_parent_drift(self):
  import subprocess,os
  from muse_guard.freeze import create_amended_manifest,verify_freeze,sha
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);folder=root/'datasets/holdout';folder.mkdir(parents=True);(root/'study').mkdir()
   data={}
   for i in range(20):
    p=folder/('h%02d.json'%i);p.write_text('{}');data[str(p.relative_to(root))]=sha(p)
   prompt=root/'prompt';prompt.write_text('original')
   original={'schema_version':1,'holdout_pair_count':20,'data_files':data,'protocol_files':{'prompt':sha(prompt)},'quality_gate':[]}
   old=folder/'MANIFEST.json';old.write_text(json.dumps(original));old_bytes=old.read_bytes()
   env={'PATH':os.environ['PATH'],'HOME':directory,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_NOSYSTEM':'1'}
   def git(*args):return subprocess.check_output(['git',*args],cwd=root,env=env,stderr=subprocess.DEVNULL)
   def commit(message):git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-m',message)
   git('init','-b','main');commit('original freeze')
   with patch('muse_guard.freeze.ROOT',root),patch('muse_guard.freeze.LOCKED_FILES',('prompt',)):
    prompt.write_text('approved amendment')
    manifest=create_amended_manifest();active=root/'study/MANIFEST-day4.json';active.write_text(json.dumps(manifest))
    with self.assertRaisesRegex(ValueError,'anchor'):verify_freeze()
    commit('amended freeze')
    self.assertEqual(verify_freeze()['protocol'],'UNCHANGED');self.assertEqual(old.read_bytes(),old_bytes)
    prompt.write_text('unapproved change')
    with self.assertRaisesRegex(ValueError,'drift'):verify_freeze()
    prompt.write_text('approved amendment');old.write_text('{}')
    with self.assertRaisesRegex(ValueError,'original commit'):verify_freeze()
