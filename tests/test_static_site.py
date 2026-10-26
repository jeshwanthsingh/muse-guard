import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/recovery-289db424fb09-view-day5.json'

class StaticSiteTests(unittest.TestCase):
 def test_export_is_local_read_only_and_downloads_public_evidence(self):
  from muse_guard.site import export_site
  before=SOURCE.read_bytes()
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/'site'
   with patch('muse_guard.recovery.resume_recovery',side_effect=AssertionError('No live mode')):
    export_site([SOURCE],out)
   index=(out/'index.html').read_text();page=next((out/'runs').glob('*.html')).read_text()
   record=json.loads(next((out/'evidence').glob('*.json')).read_text())
   self.assertIn('Recorded run',index);self.assertIn('Recorded run',page)
   self.assertIn('Refund policy',index);self.assertIn('RECOVERED',index)
   self.assertIn('Download evidence record',page);self.assertIn('../evidence/',page)
   for forbidden in ('<script','<button','<form','data-winner','data-decision-token','/decision','/view.js'):
    self.assertNotIn(forbidden,page)
   for field in ('budget_events','session_id','child_exports','source_export_sha256'):
    self.assertNotIn(field,json.dumps(record))
   self.assertEqual(record['repair']['outcome'],'PASS');self.assertEqual(record['cost_usd'],json.loads(before)['cost_usd'])
   self.assertEqual(record['publication']['kind'],'public evidence extract')
   self.assertEqual(SOURCE.read_bytes(),before)
   with self.assertRaises(ValueError):export_site([SOURCE],out)
 def test_private_metadata_is_dropped_and_private_display_content_rejected(self):
  from muse_guard.site import public_record,scan_text
  row=json.loads(SOURCE.read_text());row['env']={'META_API_KEY':'planted-sensitive-value'}
  row['attempt']['budget_events']=[{'secret':'planted-sensitive-value'}]
  clean=public_record(row,'a'*64)
  self.assertNotIn('planted-sensitive-value',json.dumps(clean))
  for secret in ('/Users/private-owner/.env','/home/private-owner/.ssh','laptop.tail123.ts.net','machine.local','https://private.example/path','META_API_KEY=planted-sensitive-value'):
   with self.subTest(secret=secret),self.assertRaises(ValueError):scan_text(secret)
 def test_unsafe_record_ids_duplicates_and_injected_public_secrets_fail_atomically(self):
  from muse_guard.site import export_site
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);source=root/'input.json';out=root/'site'
   for identity in ('../escape','a/b','bad name'):
    row=json.loads(SOURCE.read_text());row['recovery_id']=identity;source.write_text(json.dumps(row))
    with self.assertRaises(ValueError):export_site([source],out)
    self.assertFalse(out.exists())
   row=json.loads(SOURCE.read_text());row['conflict_card']['text']='META_API_KEY=planted-sensitive-value';source.write_text(json.dumps(row))
   with self.assertRaises(ValueError):export_site([source],out)
   self.assertFalse(out.exists())
   with self.assertRaises(ValueError):export_site([SOURCE,SOURCE],out)
   self.assertFalse(out.exists())
 def test_planted_label_is_explicit_and_no_recovery_controls_on_pass(self):
  from muse_guard.site import export_site
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);source=root/'fixture.json'
   source.write_text(json.dumps({'run_id':'planted-cheat','task':'refund-solvable','outcome':'UNAUTHORIZED TEST CHANGE','planted':True,'fixture_description':'Deliberately edited original test.','model_invoked':False,'cost_usd':0,'tests':[{'id':'OriginalTests.test_one','layer':'visible','status':'FAIL'}]}))
   export_site([source],root/'site')
   page=(root/'site/runs/planted-cheat.html').read_text();index=(root/'site/index.html').read_text()
   self.assertIn('Planted fixture',page);self.assertIn('Planted fixture',index)
   self.assertIn('not observed Muse behavior',page)
   self.assertNotIn('Which rule should take precedence?',page)

 def test_all_curated_examples_have_valid_relative_links_and_no_live_elements(self):
  from html.parser import HTMLParser
  from muse_guard.site import export_site
  class Links(HTMLParser):
   def __init__(self):super().__init__();self.links=[];self.tags=[]
   def handle_starttag(self,tag,attrs):
    self.tags.append(tag)
    self.links.extend(v for k,v in attrs if k in ('href','src'))
  sources=sorted((ROOT/'demo/records').glob('*.json'))
  self.assertEqual(len(sources),4)
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/'site';export_site(sources,out)
   pages=list(out.rglob('*.html'));self.assertEqual(len(pages),5)
   for page in pages:
    parser=Links();parser.feed(page.read_text())
    self.assertFalse({'script','button','form','iframe'} & set(parser.tags))
    for link in parser.links:
     if link.startswith('#'):continue
     if link.startswith('data:application/json;base64,'):
      import base64
      payload=base64.b64decode(link.split(',',1)[1])
      self.assertIn(payload,[p.read_bytes() for p in (out/'evidence').glob('*.json')]);continue
     self.assertFalse(link.startswith(('/','http:','https:','javascript:')))
     target=(page.parent/link).resolve()
     self.assertTrue(target.is_relative_to(out.resolve()));self.assertTrue(target.is_file())
   fixture=json.loads((out/'evidence/planted-edited-test.json').read_text())
   self.assertTrue(fixture['planted']);self.assertFalse(fixture['model_invoked'])
   self.assertEqual(fixture['cost_usd'],0);self.assertNotEqual(fixture['outcome'],'PASS')
 def test_pages_workflow_cannot_deploy_when_dispatched(self):
  source=(ROOT/'.github/workflows/pages.yml').read_text()
  self.assertIn('workflow_dispatch:',source);self.assertIn('if: ${{ false }}',source)
  self.assertNotIn('  push:',source)
