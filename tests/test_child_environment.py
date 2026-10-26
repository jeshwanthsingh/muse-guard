"""Offline planted secrets: both child boundaries must drop parent credentials."""
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest.mock import patch

from muse_guard.checker import _observe
from muse_guard.gateway import Gateway
from muse_guard.runner import run_one
from muse_guard.rules import TASKS

CANARIES = {"META_API_KEY": "planted-provider-value", "MODEL_API_KEY": "planted-other-key",
            "DATABASE_URL": "planted-database-value", "ARBITRARY_ENV_VALUE": "planted-arbitrary-value",
            "NODE_OPTIONS": "planted-node-options", "PYTHONPATH": "planted-python-path"}

@unittest.skipUnless(platform.system() == "Darwin", "Requires the production macOS sandbox")
class ChildEnvironmentTests(unittest.TestCase):
    def test_candidate_printing_environment_has_no_parent_dotenv_values(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, CANARIES):
            solution = Path(directory) / "solution.py"
            solution.write_text("import json, os, sys\ndef solve(value):\n print(json.dumps(dict(os.environ)), file=sys.stderr)\n return dict(os.environ)\n")
            child = _observe(solution, None)
        self.assertFalse(set(CANARIES) & set(child))
        self.assertFalse(set(CANARIES.values()) & set(child.values()))
        self.assertLessEqual(set(child), {"PATH", "HOME", "TMPDIR", "LANG", "LC_CTYPE"})

    def test_muse_version_exec_and_export_drop_parent_values_and_use_dummy_stdin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); cli = root / "bin"; cli.mkdir()
            executable = cli / "muse"
            executable.write_text("#!" + sys.executable + "\n" + """
import json, os, pathlib, sys
args=sys.argv[1:]
packet={'environment':dict(os.environ)}
if args == ['--version']:
    print('Muse Code 1.4.2 (1.4.2-R4684.1)')
elif args[0] == 'exec':
    packet['stdin']=sys.stdin.read()
    packet['args']=args
    pathlib.Path('muse-environment.json').write_text(json.dumps(packet))
elif args[0] == 'export':
    packet['events']=[]
    pathlib.Path(args[args.index('--out')+1]).write_text(json.dumps(packet))
else:
    sys.exit(2)
""")
            executable.chmod(0o755)
            parent = dict(CANARIES, PATH=str(cli)+os.pathsep+os.defpath)
            from muse_guard.runner import run_process
            seen=[]
            def observe_process(args,cwd,env,**kwargs):
                seen.append(dict(env))
                return run_process(args,cwd,env,**kwargs)
            with patch('muse_guard.runner.run_process',side_effect=observe_process), patch('muse_guard.runner.Gateway', wraps=Gateway) as gate:
                record=run_one(TASKS['retry-solvable'],root/'results',env=parent)
            raw=root/'results/raw'/record['run_id']
            packet=json.loads((raw/'frozen/muse-environment.json').read_text())
            exported=json.loads((raw/'session.json').read_text())
            for child in seen+[packet['environment'],exported['environment']]:
                self.assertFalse(set(CANARIES) & set(child))
                self.assertFalse(set(parent.values()) & set(child.values()))
            self.assertEqual(len(seen),3)
            self.assertIn('--api-key-stdin',packet['args'])
            self.assertEqual(packet['stdin'],'proxy-only-no-provider-key\n')
            self.assertEqual(gate.call_args.args[0],CANARIES['META_API_KEY'])
            self.assertFalse(record['model_invoked'])
            self.assertEqual(record['cost_usd'],0)
