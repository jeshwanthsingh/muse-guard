import copy,hashlib,json,os,subprocess,tempfile,unittest,urllib.request
from pathlib import Path
from unittest.mock import patch
from submission_tools.baseten import MODEL,BASE,BasetenGateway,chat_request,configuration,child_environment
from submission_tools.check_protected import verify
ROOT=Path(__file__).resolve().parents[1]

class SubmissionTests(unittest.TestCase):
 def test_actual_protected_baseline_unchanged(self):self.assertEqual(verify()['status'],'UNCHANGED')
 def test_guard_rejects_worktree_and_staged_drift(self):
  from submission_tools import check_protected as guard
  for where in ('worktree','staged'):
   with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);(root/'submission_tools').mkdir();(root/'spec_eval').mkdir()
    original=b'{}';h=hashlib.sha256(original).hexdigest()
    (root/'spec_eval/MANIFEST.json').write_bytes(b'changed' if where=='worktree' else original)
    (root/'submission_tools/protected.json').write_text(json.dumps({'base_commit':guard.BASE,'files':{'spec_eval/MANIFEST.json':h}}))
    def fake(*args,**kwargs):
     if args[0]=='ls-files':return b'spec_eval/MANIFEST.json\n'
     if args[1].endswith('results/SPEC_VERIFICATION.json'):return b'{"protected_baseline_sha256":{}}'
     if args[1]==guard.BASE+':spec_eval/MANIFEST.json':return original
     return b'changed' if where=='staged' else original
    # The source manifest must contain files for coverage; use a valid empty one.
    original=b'{"files":{}}';h=hashlib.sha256(original).hexdigest()
    (root/'submission_tools/protected.json').write_text(json.dumps({'base_commit':guard.BASE,'files':{'spec_eval/MANIFEST.json':h}}))
    (root/'spec_eval/MANIFEST.json').write_bytes(b'changed' if where=='worktree' else original)
    with patch.object(guard,'git',side_effect=fake):
     with self.assertRaisesRegex(ValueError,where):guard.verify(root)
 def test_submission_export_only_changes_presentation(self):
  from submission_tools.export_demo import export
  with tempfile.TemporaryDirectory() as directory:
   out=export(Path(directory)/'site');page=(out/'index.html').read_text()
   for text in ('Refund policy - conflict','Refund policy - normal task','GitHub','Clash found','muse-guard finds every conflicting action among the confirmed rules and declared inputs'):self.assertIn(text,page)
   for p in (out/'evidence').glob('*.json'):self.assertEqual(p.read_bytes(),(ROOT/'output/judge-site/evidence'/p.name).read_bytes())
   for p in out.rglob('*.html'):
    text=p.read_text();self.assertNotIn('<script',text);self.assertNotIn('<form',text)
 def test_only_hackathon_model_and_text_tools_translated(self):
  request=chat_request({'model':'wrong','input':[{'type':'function_call','call_id':'c','name':'shell','arguments':'{}'},{'type':'function_call_output','call_id':'c','output':'ok'}],'tools':[{'type':'function','name':'shell','parameters':{}}]})
  self.assertEqual(request['model'],MODEL);self.assertEqual(request['messages'][1]['role'],'tool')
  self.assertEqual(request['tools'][0]['function']['name'],'shell')
  for data in ({'previous_response_id':'r'},{'input':[{'type':'reasoning'}]},{'tools':[{'type':'web_search'}]}):
   with self.assertRaises(ValueError):chat_request(data)
 def test_baseten_usage_stream_and_private_environment(self):
  from muse_guard.runner import usage_from_export
  calls=[]
  def transport(data):
   calls.append(data);return {'choices':[{'finish_reason':'stop','message':{'content':'done'}}],
    'usage':{'prompt_tokens':100,'completion_tokens':10,'prompt_tokens_details':{'cached_tokens':50}}}
  with tempfile.TemporaryDirectory() as directory:
   journal=Path(directory)/'usage.json'
   with BasetenGateway('planted-secret',chat_transport=transport,count_tokens=lambda _:100,token_limit=4096,dollar_limit='.02',journal=journal) as gateway:
    req=urllib.request.Request(gateway.url+'/responses',data=json.dumps({'input':'hi','stream':True}).encode(),headers={'Content-Type':'application/json'})
    body=urllib.request.urlopen(req).read().decode()
   self.assertIn('response.completed',body);self.assertNotIn('planted-secret',body+journal.read_text())
   event=json.loads(journal.read_text())['requests'][0];self.assertEqual(event['model'],MODEL)
   tokens,cost=usage_from_export({'usage':event['usage']});self.assertAlmostEqual(cost,.0001125)
   self.assertEqual(calls[0]['model'],MODEL)
 def test_missing_usage_blocks_subsequent_request(self):
  calls=[]
  def transport(data):calls.append(data);return {'choices':[{'finish_reason':'stop','message':{'content':'ok'}}]}
  with BasetenGateway('fake',chat_transport=transport,count_tokens=lambda _:10,token_limit=4096,dollar_limit='.02') as gate:
   def req():return urllib.request.urlopen(urllib.request.Request(gate.url+'/responses',data=b'{"input":"hi"}',headers={'Content-Type':'application/json'})).read()
   req()
   with self.assertRaises(urllib.error.HTTPError) as caught:req()
   caught.exception.close()
  self.assertEqual(len(calls),1)
 def test_key_and_arbitrary_env_never_reach_child_or_candidate(self):
  from muse_guard.checker import _observe
  secrets={'BASETEN_API_KEY':'planted-baseten-secret','META_API_KEY':'planted-meta-secret','BASETEN_BASE_URL':BASE,'ARBITRARY_DOTENV':'planted-other-value'}
  with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,secrets):
   root=Path(directory)
   text=subprocess.check_output(['/usr/bin/env'],env=child_environment(root),text=True)
   candidate=root/'solution.py';candidate.write_text('import os\ndef solve(x):\n return str(dict(os.environ))\n')
   result=_observe(candidate,{})
   for value in secrets.values():self.assertNotIn(value,text+str(result))
 def test_invalid_endpoint_and_live_calls_fail_closed(self):
  with self.assertRaises(ValueError):configuration({'BASETEN_API_KEY':'x','BASETEN_BASE_URL':'https://attacker.example/v1'})
  with self.assertRaisesRegex(ValueError,'Live Baseten blocked'):BasetenGateway('x')
 def test_day6_receipts_bind_results_without_mutating_them(self):
  from submission_tools.study_receipts import capture,PIN
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)/'repo';(root/'results').mkdir(parents=True);p=root/'results/new.json';raw=b'{"run_id":"new","outcome":"PASS"}';p.write_bytes(raw)
   with patch('submission_tools.study_receipts.verify',return_value=PIN):self.assertEqual(capture(root,Path(directory)/'receipts',{}),1)
   row=json.loads((Path(directory)/'receipts/new.json').read_text());self.assertEqual(row['runtime_commit'],PIN);self.assertEqual(row['original_sha256'],hashlib.sha256(raw).hexdigest());self.assertEqual(p.read_bytes(),raw)
 def test_day6_wrapper_rejects_submission_runtime(self):
  from submission_tools.study_receipts import verify as study_verify
  with self.assertRaisesRegex(ValueError,'exactly'):study_verify(ROOT)

 def test_real_muse_cli_tiny_turn_uses_only_fake_baseten_transport(self):
  import shutil
  from muse_guard.runner import run_process
  from muse_guard.isolation import author_command
  cli=shutil.which('muse')
  if not cli:self.skipTest('Muse CLI unavailable')
  calls=[]
  def transport(data):
   calls.append(data)
   return {'choices':[{'finish_reason':'stop','message':{'content':'Offline bridge checked.'}}], 'usage':{'prompt_tokens':100,'completion_tokens':10}}
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   for name in ('home','config','tmp','agent'):(root/name).mkdir()
   with BasetenGateway('fake-only',chat_transport=transport,count_tokens=lambda _:100,token_limit=160000,dollar_limit='.5') as gate:
    args=[cli,'exec','--api-key-stdin','--provider','meta','--model','muse-spark-1.3','--base-url',gate.url,'--preset','miniswe','--reasoning-effort','low','--max-model-steps','2','--disable-web-tools','--no-foreign-personal-context','--disable-sandbox','--disable-approval','--approval-judge','off','--workspace',str(root/'agent'),'--json','Say offline bridge checked; do not use tools.']
    result=run_process(author_command(args,write_root=root,gateway_url=gate.url),root/'agent',child_environment(root),timeout=25,input_data=b'proxy-only-no-provider-key\n')
   self.assertTrue(calls,result.stdout+result.stderr)
   self.assertIn('Offline bridge checked.',result.stdout)
   self.assertTrue(all(r['model']==MODEL for r in calls))

 def test_namespace_tool_names_roundtrip_and_collisions_refused(self):
  from submission_tools.baseten import translated_tools,response
  data={'tools':[{'type':'namespace','name':'muse','tools':[{'type':'function','name':'bash','parameters':{}}]}]}
  tools,mapping=translated_tools(data)
  self.assertEqual(tools[0]['function']['name'],'muse__bash')
  row=response({'choices':[{'finish_reason':'tool_calls','message':{'tool_calls':[{'id':'call1','type':'function','function':{'name':'muse__bash','arguments':'{}'}}]}}]},mapping)
  self.assertEqual(row['output'][0]['name'],'muse.bash')
  data['tools'].append({'type':'function','name':'muse__bash'})
  with self.assertRaises(ValueError):translated_tools(data)

 def test_https_transport_auth_and_errors_do_not_expose_credentials(self):
  from submission_tools.baseten import BasetenTransport
  from unittest.mock import MagicMock
  opener=MagicMock();reply=opener.open.return_value.__enter__.return_value
  reply.read.return_value=b'{"choices":[]}'
  with patch('submission_tools.baseten.urllib.request.build_opener',return_value=opener):
   self.assertEqual(BasetenTransport('planted-key',BASE)({'model':MODEL}),{'choices':[]})
   req=opener.open.call_args.args[0]
   self.assertEqual(req.get_header('Authorization'),'Bearer planted-key')
   self.assertEqual(req.full_url,BASE+'/chat/completions')
   opener.open.side_effect=ValueError('planted-key must not escape')
   with self.assertRaises(ValueError) as caught:BasetenTransport('planted-key',BASE)({})
   self.assertNotIn('planted-key',str(caught.exception))
