import copy,json,tempfile,unittest
from pathlib import Path
from submission_tools.export_policy import phase_failure,export_session
ROOT=Path(__file__).resolve().parents[1]
class ExportPolicyTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.row=json.loads((ROOT/'study_runs/holdout-2026-10-27/h13-b-v1-0c28f4f6a26e.json').read_text())
  self.raw=self.root/'raw'/self.row['run_id'];self.raw.mkdir(parents=True)
  self.journal=self.raw/'provider-usage.json';self.journal.write_text(json.dumps({'requests':self.row['budget_events']}))
 def test_missing_reminder_exports_with_complete_journal_accepted(self):
  self.assertIsNone(phase_failure(self.row,self.root))
 def test_root_failure_fatal(self):
  self.row['export_exit_code']=1;self.assertEqual(phase_failure(self.row,self.root),'session export failure')
 def test_unknown_usage_fatal(self):
  self.row['cost_usd']=None;self.assertEqual(phase_failure(self.row,self.root),'missing provider usage')
 def test_missing_receipt_fatal(self):
  self.journal.write_text('{"requests":[]}');self.assertEqual(phase_failure(self.row,self.root),'provider journal mismatch')
 def test_invalid_usage_fatal(self):
  self.row['budget_events'][0]['usage']['input_tokens']=-1;self.journal.write_text(json.dumps({'requests':self.row['budget_events']}))
  self.assertEqual(phase_failure(self.row,self.root),'invalid provider usage')
 def test_full_stderr_and_exit_preserved(self):
  cli=self.root/'fake';cli.write_text('#!/bin/sh\nprintf "missing session\\n" >&2\nexit 1\n');cli.chmod(0o755)
  result=export_session(str(cli),'missing',self.root/'out.json',self.root,{})
  self.assertEqual(result.returncode,1);self.assertEqual((self.root/result.diagnostics['stderr_file']).read_text(),'missing session\n')
 def test_holdout_smoke_rejected(self):
  from submission_tools.export_runtime.ledger import authorize
  with self.assertRaisesRegex(ValueError,'DEV smoke only'):authorize({'split':'holdout'},True)
if __name__=='__main__':unittest.main()
