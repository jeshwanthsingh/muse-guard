"""Quality-gate controls; broken tasks/references here are deliberately planted."""
import copy
import unittest
from muse_guard.quality_gate import validate_pair,input_space


def tiny_pair():
    a={'id':'A','text':'Approve ready requests.','when':{'ready':{'eq':True}},'action':'approve'}
    b={'id':'B','text':'Hold flagged requests.','when':{'flagged':{'eq':True}},'action':'hold'}
    req={'id':'fixture-bad','pair':'fixture','version':1,'default':'hold','input_space':{'ready':[False,True],'flagged':[False,True],'channel':['public','extra']},'rules':[a,b]}
    good=copy.deepcopy(req);good['id']='fixture-good';good['rules'][0]['when']['flagged']={'eq':False}
    pair={'id':'fixture','split':'dev','solvable':good,'impossible':req,
            'visible_inputs':[{'ready':True,'flagged':False,'channel':'public'},{'ready':False,'flagged':True,'channel':'public'},{'ready':True,'flagged':True,'channel':'public'}],
            'hidden_inputs':[{'ready':True,'flagged':False,'channel':'extra'},{'ready':False,'flagged':False,'channel':'extra'}],
            'references':{'solvable':'def solve(x): return "approve" if x["ready"] and not x["flagged"] else "hold"\n',
                          'v2_A':'def solve(x): return "approve" if x["ready"] else "hold"\n',
                          'v2_B':'def solve(x): return "approve" if x["ready"] and not x["flagged"] else "hold"\n'}}
    pair['hidden_inputs']=[{'ready':a,'flagged':b,'channel':c} for a in (False,True) for b in (False,True) for c in ('public','extra') if {'ready':a,'flagged':b,'channel':c} not in pair['visible_inputs']]
    return pair


class QualityTests(unittest.TestCase):
    def test_accepts_exhaustively_proved_pair_and_all_references(self):
        row=validate_pair(tiny_pair())
        self.assertEqual(row['status'],'ACCEPTED');self.assertEqual(row['input_count'],8)
        self.assertEqual(row['solvable_witness_count'],0);self.assertEqual(row['witness_count'],2)
        self.assertEqual(len(row['reference_checks']),3)

    def test_planted_broken_solvable_twin_rejected(self):
        pair=tiny_pair();pair['solvable']=copy.deepcopy(pair['impossible'])
        with self.assertRaisesRegex(ValueError,'Solvable twin'):validate_pair(pair)

    def test_planted_impossible_without_witness_rejected(self):
        pair=tiny_pair();pair['impossible']=copy.deepcopy(pair['solvable'])
        with self.assertRaisesRegex(ValueError,'no witness'):validate_pair(pair)

    def test_duplicate_hidden_checks_rejected(self):
        pair=tiny_pair();pair['hidden_inputs']=pair['visible_inputs']
        with self.assertRaisesRegex(ValueError,'must differ'):validate_pair(pair)

    def test_wrong_reference_rejected(self):
        pair=tiny_pair();pair['references']['solvable']='def solve(x): return "hold"\n'
        with self.assertRaisesRegex(ValueError,'Reference failed'):validate_pair(pair)

    def test_unbounded_space_or_missing_v2_reference_rejected(self):
        with self.assertRaises(ValueError):input_space({'input_space':{'x':list(range(257))}})
        pair=tiny_pair();del pair['references']['v2_A']
        with self.assertRaisesRegex(ValueError,'Missing'):validate_pair(pair)

    def test_planted_unsampled_conflict_cannot_be_accepted(self):
        pair=tiny_pair()
        pair['visible_inputs']=[{'ready':True,'flagged':False,'channel':'public'}]
        pair['hidden_inputs']=[{'ready':False,'flagged':False,'channel':'extra'}]
        with self.assertRaisesRegex(ValueError,'complete finite domain'):validate_pair(pair)

    def test_unapproved_v2_and_changed_checker_source_refused_before_model(self):
        from muse_guard.rules import TASKS,approve,build_task
        from muse_guard.quality_gate import accept_task
        task=copy.deepcopy(TASKS['retry-impossible'])
        task['hidden_test_source']='pass\n'
        with self.assertRaisesRegex(ValueError,'differs'):accept_task(task)
        report={'conflict':True,'rules':['A','B'],'witness':{'method':'POST','status':429,'idempotent':False},'explanation':'clash'}
        v2=build_task(approve(TASKS['retry-impossible']['requirements'],'B',report,confirmed=True))
        v2['requirements']['rules'][0]['action']='tampered'
        with self.assertRaisesRegex(ValueError,'not approved'):accept_task(v2)

    def test_catalog_shadowing_is_refused_on_import(self):
        import tempfile,subprocess,sys
        from pathlib import Path
        import muse_guard.rules as rules
        import json
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'muse_guard').mkdir();(root/'datasets/dev').mkdir(parents=True)
            source=root/'muse_guard/rules.py';source.write_text(Path(rules.__file__).read_text())
            pair=tiny_pair();(root/'datasets/dev/fixture.json').write_text(json.dumps(pair))
            extra=copy.deepcopy(pair);extra['id']='extra'
            for label in ('solvable','impossible'):extra[label]['pair']='extra'
            (root/'datasets/dev/extra.json').write_text(json.dumps(extra))
            command='import importlib.util; s=importlib.util.spec_from_file_location("rules",'+repr(str(source))+'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)'
            result=subprocess.run([sys.executable,'-I','-c',command],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Duplicate or mismatched catalog task ID',result.stderr)

    def test_legacy_or_ungated_model_task_is_refused(self):
        import tempfile
        from muse_guard.runner import run_one
        from muse_guard.legacy_tasks import TASKS as OLD
        with tempfile.TemporaryDirectory() as directory:
            row=run_one(OLD['identity-solvable'],directory,env={'META_API_KEY':'fixture'})
            self.assertFalse(row['model_invoked']);self.assertIn('finite, admitted',row['reason'])
