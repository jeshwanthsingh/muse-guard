"""Offline JS/Python parity and evidence immutability for the judge playground."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from muse_guard.quality_gate import input_space
from muse_guard.rules import verify_conflict
from submission_tools.judge_demo import ASSETS, demo_tables

ROOT = Path(__file__).resolve().parents[1]


def python_search(table):
    clashes = []
    rules = [r for r in table['rules'] if r.get('enabled', True)]
    req = dict(table, rules=rules)
    space = input_space(req)
    for witness in space:
        for a, b in itertools.combinations(rules, 2):
            proof = verify_conflict(req, {'conflict': True, 'rules': [a['id'], b['id']],
                                        'witness': witness, 'explanation': 'Parity test'})
            if proof['verified']:
                clashes.append({k: proof[k] for k in ('witness', 'rules', 'actions')})
    return {'checked': len(space), 'clashes': clashes}


def parity_cases():
    cases = []
    for original in demo_tables():
        # Every subset and equality pattern, plus a newly typed action.
        actions = list(dict.fromkeys(r['action'] for r in original['rules'])) + ['new_next_action']
        for enabled in itertools.product((False, True), repeat=len(original['rules'])):
            for edited in itertools.product(actions, repeat=len(original['rules'])):
                table = copy.deepcopy(original)
                for rule, on, action in zip(table['rules'], enabled, edited):
                    rule.update(enabled=on, action=action)
                cases.append({'table': table, 'expected': python_search(table)})
    return cases


class JudgeDemoTests(unittest.TestCase):
    def test_javascript_matches_python_on_every_demo_table_and_all_editor_states(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node is required for the browser search regression')
        cases = parity_cases()
        script = "const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync(process.argv[1],'utf8'));const cases=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(cases.map(c=>MuseGuardClashes.search(c.table))));"
        actual = json.loads(subprocess.check_output([node, '-e', script, str(ASSETS/'clashes.js')], input=json.dumps(cases).encode()))
        self.assertEqual(len(cases), 144)
        self.assertEqual(actual, [c['expected'] for c in cases])
        self.assertTrue(any(c['expected']['clashes'] for c in cases))
        self.assertTrue(any(not c['expected']['clashes'] for c in cases))

    def test_results_match_completed_study_and_no_overclaim(self):
        from submission_tools.judge_demo import RESULTS
        summary = json.loads((ROOT/'study_runs/holdout-third-2026-10-27/summary.json').read_text())
        a, b = (summary['primary_results'][m] for m in ('plain', 'guarded'))
        self.assertEqual((a['flows']+b['flows'], a['recoveries'], b['recoveries']), (160,39,40))
        for row in (a,b):
            for key in ('claim_contradicted_attempts','original_tests_edited_attempts','visible_pass_hidden_fail_repairs'):
                self.assertEqual(row[key],0)
        self.assertAlmostEqual((b['known_cost_usd']/a['known_cost_usd']-1)*100,1.643,places=2)
        self.assertAlmostEqual((b['coding_steps_known']/a['coding_steps_known']-1)*100,9.369,places=2)
        for text in ('not a proven advantage','strict 7/10','0 false','representation','20 holdout pairs'):
            self.assertIn(text, RESULTS)

    def test_export_preserves_recordings_and_uses_only_local_scripts(self):
        from submission_tools.export_demo import export
        with tempfile.TemporaryDirectory() as directory:
            out=export(Path(directory)/'site')
            index=(out/'index.html').read_text()
            for asset in ('editor.js','clashes.js','tables.js','editor.css','results.html'):
                self.assertTrue((out/asset).is_file())
            self.assertIn("connect-src 'none'",index)
            self.assertIn('Interactive example',index)
            self.assertIn('never change recorded runs',index)
            for forbidden in ('/decision','data-winner','fetch(', 'XMLHttpRequest','WebSocket','localStorage'):
                for name in ('index.html','editor.js','clashes.js'):
                    self.assertNotIn(forbidden,(out/name).read_text())
            manifest=json.loads((out/'manifest.json').read_text())
            for name,sha in manifest['files'].items():
                self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),sha)
            for source in (ROOT/'output/judge-site/evidence').glob('*.json'):
                self.assertEqual(source.read_bytes(),(out/'evidence'/source.name).read_bytes())
            for page in (out/'runs').glob('*.html'):
                self.assertNotIn('<script',page.read_text())
                self.assertNotIn('<button',page.read_text())
