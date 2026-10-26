"""Offline UI fixtures. No real model calls or decisions."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'results/recovery-289db424fb09.json'

class ViewTests(unittest.TestCase):
 def test_refund_record_renders_in_evidence_order_and_preserves_verdict(self):
  from muse_guard.view import render
  row=json.loads(RECORD.read_text());before=copy.deepcopy(row)
  page=render(row,diff_text='- old\n+ repaired')
  headings=['Task and rules','Conflict card','Developer decision','Repair diff','Independent checks','Download evidence record']
  positions=[page.index(x) for x in headings]
  self.assertEqual(positions,sorted(positions));self.assertEqual(row,before)
  for text in ['Recorded run','Verified by checker','Rule A wins','Rule B wins','manual_review','HiddenTests.test_hidden_000','RECOVERED']:
   self.assertIn(text,page)
  self.assertIn('disabled',page)
 def test_unverified_and_hostile_record_does_not_get_badge_or_html_execution(self):
  from muse_guard.view import render
  row=json.loads(RECORD.read_text());row['conflict_validation']['verified']=False
  row['conflict_card']['text']='<script>alert(1)</script>'
  page=render(row)
  self.assertNotIn('Verified by checker',page);self.assertNotIn('<script>alert(1)</script>',page)
  self.assertIn('&lt;script&gt;',page)
 def test_saved_artifact_diff_is_verified_and_missing_is_explicit(self):
  from muse_guard.view import repair_diff
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);row={'attempt':{'run_id':'before'},'repair':{'run_id':'after'}}
   for phase,source in [('attempt','def solve(x): raise NotImplementedError()\n'),('repair','def solve(x): return "manual_review"\n')]:
    folder=root/'raw'/row[phase]['run_id']/'frozen';folder.mkdir(parents=True)
    (folder/'solution.py').write_text(source)
    row[phase]['frozen_sha256']={'solution.py':hashlib.sha256(source.encode()).hexdigest()}
   diff=repair_diff(row,root)
   self.assertIn('manual_review',diff);self.assertIn('NotImplementedError',diff)
   row['repair']['frozen_sha256']['solution.py']='0'*64
   self.assertIn('unavailable',repair_diff(row,root))
 def test_standalone_attempt_resolves_only_hash_matching_rules(self):
  from muse_guard.view import render
  row=json.loads((ROOT/'results/refund-solvable-v1-4c0c358c42bd.json').read_text())
  self.assertIn('Refund eligible purchases.',render(row))
  row['requirements_hash']='0'*64
  self.assertNotIn('Refund eligible purchases.',render(row))
 def test_http_download_replay_and_cross_origin_guard(self):
  from muse_guard.view import create_server
  server=create_server(RECORD)
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  base='http://127.0.0.1:'+str(server.server_port)
  try:
   with urllib.request.urlopen(base+'/evidence.json') as response:self.assertEqual(response.read(),RECORD.read_bytes())
   with urllib.request.urlopen(base+'/') as response:self.assertIn(b'Recorded run',response.read())
   with self.assertRaises(urllib.error.HTTPError) as error:
    urllib.request.urlopen(urllib.request.Request(base+'/decision',data=b'{"winner":"B"}',headers={'Content-Type':'application/json'}))
   self.assertEqual(error.exception.code,403);error.exception.close()
   with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+'/.env')
   self.assertEqual(error.exception.code,404);error.exception.close()
  finally:server.shutdown();server.server_close();thread.join()
 def test_live_requires_verified_awaiting_record(self):
  from muse_guard.view import create_server
  with self.assertRaises(ValueError):create_server(RECORD,live=True)

class ResumeTests(unittest.TestCase):
 def prepare(self,directory):
  row=json.loads(RECORD.read_text());row['status']='AWAITING DECISION'
  for field in ['repair','requirements_v2','decision','v2_tests_hash']:row.pop(field,None)
  row['phase_run_ids']=row['phase_run_ids'][:2]
  root=Path(directory);self.enterContext(patch('muse_guard.recovery.RESULTS_ROOT',root));path=root/'recovery-fixture.json';row['recovery_id']='recovery-fixture'
  raw=root/'raw'/row['attempt']['run_id']/'frozen';raw.mkdir(parents=True)
  source=b'def solve(x):\n raise NotImplementedError()\n';(raw/'solution.py').write_bytes(source)
  row['attempt']['frozen_sha256']['solution.py']=hashlib.sha256(source).hexdigest()
  path.write_text(json.dumps(row));return path,row
 def test_live_choice_uses_approved_v2_checker_and_is_single_use(self):
  from muse_guard.recovery import resume_recovery
  with tempfile.TemporaryDirectory() as directory:
   path,row=self.prepare(directory)
   def run(task,results,env,**kw):
    self.assertEqual(task['requirements']['priority'][0],'B');self.assertIn(b'NotImplementedError',kw['seed_solution'])
    return {'run_id':'offline-repair','outcome':'PASS','tests':[],'tokens':{'input':0,'output':0,'cached_input':0},'cost_usd':0}
   with patch('muse_guard.recovery.run_one',side_effect=run):
    result=resume_recovery(path,'B',env={})
   self.assertEqual(result['status'],'RECOVERED');self.assertEqual(result['decision']['winner'],'B')
   with self.assertRaises(ValueError):resume_recovery(path,'A',env={})
 def test_invalid_or_unverified_decisions_do_not_run_model(self):
  from muse_guard.recovery import resume_recovery
  with tempfile.TemporaryDirectory() as directory:
   path,row=self.prepare(directory)
   with patch('muse_guard.recovery.run_one') as run:
    with self.assertRaises(ValueError):resume_recovery(path,'C',env={})
    row['conflict_report']['witness']['eligible']=False;path.write_text(json.dumps(row))
    with self.assertRaises(ValueError):resume_recovery(path,'B',env={})
    run.assert_not_called()
 def test_budget_refusal_does_not_bypass_live_resume(self):
  from muse_guard.recovery import resume_recovery
  from datetime import datetime
  from zoneinfo import ZoneInfo
  with tempfile.TemporaryDirectory() as directory:
   path,row=self.prepare(directory);root=Path(directory)
   (root/'prior.json').write_text(json.dumps({'run_id':'prior','date':datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat(),'cost_usd':4.9}))
   result=resume_recovery(path,'B',env={'META_API_KEY':'fixture'})
   self.assertEqual(result['repair']['outcome'],'HARNESS ERROR');self.assertFalse(result['repair']['model_invoked'])
   self.assertIn('$5',result['repair']['reason'])

 def test_live_http_requires_token_origin_and_refuses_second_choice(self):
  from muse_guard.view import create_server
  import re
  with tempfile.TemporaryDirectory() as directory:
   path,row=self.prepare(directory)
   server=create_server(path,live=True,env={});thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   base='http://127.0.0.1:'+str(server.server_port)
   try:
    with urllib.request.urlopen(base+'/') as response:page=response.read().decode()
    token=re.search('data-decision-token="([^"]+)"',page).group(1)
    def post(token,origin):
     return urllib.request.urlopen(urllib.request.Request(base+'/decision',data=b'{"winner":"B"}',headers={'Content-Type':'application/json','Origin':origin,'X-Decision-Token':token}))
    def fake_run(task,results,env,**kwargs):
     return {'run_id':'offline-repair','outcome':'PASS','tests':[],'tokens':{'input':0,'output':0,'cached_input':0},'cost_usd':0}
    with patch('muse_guard.recovery.run_one',side_effect=fake_run) as run:
     for key,origin in [('wrong',base),(token,'http://foreign.invalid')]:
      with self.assertRaises(urllib.error.HTTPError) as error:post(key,origin)
      self.assertEqual(error.exception.code,403);error.exception.close()
     run.assert_not_called()
     with post(token,base) as response:self.assertEqual(json.load(response)['status'],'RECOVERED')
     with self.assertRaises(urllib.error.HTTPError) as error:post(token,base)
     self.assertEqual(error.exception.code,409);error.exception.close()
     self.assertEqual(run.call_count,1)
   finally:server.shutdown();server.server_close();thread.join()

 def test_external_copy_cannot_get_a_fresh_spending_ledger(self):
  from muse_guard.recovery import resume_recovery
  import shutil
  with tempfile.TemporaryDirectory() as canonical,tempfile.TemporaryDirectory() as external:
   path,row=self.prepare(canonical);root=Path(canonical)
   (root/'spent.json').write_text(json.dumps({'run_id':'spent','cost_usd':5}))
   copied=Path(external)/path.name;shutil.copytree(root,Path(external),dirs_exist_ok=True)
   with patch('muse_guard.recovery.run_one') as run:
    with self.assertRaisesRegex(ValueError,'canonical'):resume_recovery(copied,'B',env={})
    run.assert_not_called()
