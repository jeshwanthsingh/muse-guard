import copy
import json
from pathlib import Path
import tempfile
import unittest
from spec_guard.core import validate,review,clashes,load_confirmed

ROOT=Path(__file__).resolve().parents[1]
def fixture(name='refunds'):
    return ((ROOT/'spec_eval/docs'/(name+'.md')).read_text(),json.loads((ROOT/'spec_eval/truth'/(name+'.json')).read_text()))

class SpecValidationTests(unittest.TestCase):
    def test_invented_quote_is_retained_but_cannot_be_confirmed(self):
        doc,truth=fixture();p=truth['proposal'];p['rules'][0]['quote']='Refund every order immediately.'
        row=review(doc,p,lambda item:True)
        self.assertFalse(row['validation']['items'][0]['valid'])
        self.assertEqual(row['decisions'][0]['decision'],"couldn't convert")
        self.assertEqual([r['id'] for r in row['confirmed']['rules']],['B'])
        self.assertIn('Refund every order immediately.',json.dumps(row))
    def test_missing_field_domain_rejects_rule_and_never_invents_domain(self):
        doc,truth=fixture();p=truth['proposal'];del p['input_space']['fraud_hold']
        row=review(doc,p,lambda item:True)
        self.assertFalse(row['validation']['items'][1]['valid'])
        self.assertNotIn('fraud_hold',row['confirmed']['input_space'])
        self.assertEqual(row['clashes'],[])
    def test_wrong_translation_is_rejected_by_developer(self):
        doc,truth=fixture();p=truth['proposal'];p['rules'][0]['action']='deny'
        row=review(doc,p,lambda item:item['key']!='rule-1')
        self.assertTrue(row['validation']['items'][0]['valid'])
        self.assertEqual(row['decisions'][0]['decision'],'rejected')
        self.assertNotIn('A',[r['id'] for r in row['confirmed']['rules']])
    def test_no_clashes_and_hand_written_clash_lists(self):
        for name in ('refunds','access','shipping','notifications','retention','bookings','pricing','support'):
            doc,truth=fixture(name);row=review(doc,truth['proposal'],lambda item:True)
            self.assertTrue(all(i['valid'] for i in row['validation']['items']),row)
            observed=[{k:c[k] for k in ('witness','rules','actions')} for c in row['clashes']]
            self.assertEqual(observed,truth['clashes']);self.assertEqual(row['uncovered_inputs'],[])
    def test_oversized_domain_and_wrong_types_fail_closed(self):
        doc,truth=fixture();p=truth['proposal'];p['input_space']['eligible']=list(range(9))
        row=review(doc,p,lambda item:True)
        self.assertEqual(row['confirmed']['rules'],[]);self.assertTrue(row['validation']['errors'])
    def test_unconverted_and_unrepresented_source_sentences_are_visible(self):
        doc,truth=fixture();p=truth['proposal'];missing=p['rules'].pop()
        row=review(doc,p,lambda item:True)
        self.assertIn(missing['quote'],[x['quote'] for x in row['validation']['unconverted']])
    def test_all_rule_pairs_and_witnesses_are_enumerated(self):
        doc,truth=fixture();p=truth['proposal'];p['rules'].append(dict(p['rules'][0],id='C',action='third'))
        row=review(doc,p,lambda item:True)
        self.assertEqual(len(row['clashes']),4)
    def test_receipt_changes_cannot_authorize_new_rules(self):
        doc,truth=fixture();row=review(doc,truth['proposal'],lambda item:True)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'confirmed.yaml';p.write_text(json.dumps(row['confirmed']));(root/'record.json').write_text(json.dumps(row))
            self.assertEqual(load_confirmed(p)[0],row['confirmed'])
            changed=copy.deepcopy(row['confirmed']);changed['rules'][0]['action']='different';p.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):load_confirmed(p)

class SpecIntegrationTests(unittest.TestCase):
    def test_wrong_extraction_fails_even_when_clash_is_found(self):
        from spec_guard.evaluation import score
        doc,truth=fixture();proposal=copy.deepcopy(truth['proposal']);proposal['default']['action']='invented_action'
        measured,_=score(doc,proposal,truth)
        self.assertEqual(measured['clashes_found'],1)
        self.assertFalse(measured['extraction_success']);self.assertEqual(measured['wrong_rules'],1)
    def test_wrong_rule_can_create_a_false_clash(self):
        from spec_guard.evaluation import score
        doc,truth=fixture('shipping');proposal=copy.deepcopy(truth['proposal']);del proposal['rules'][0]['when']['hazardous']
        measured,_=score(doc,proposal,truth)
        self.assertFalse(measured['extraction_success']);self.assertEqual(measured['false_clashes'],1)
    def test_viewer_escapes_doc_and_retains_failed_rows(self):
        from spec_guard.view import render
        doc,truth=fixture();doc='<script>alert(1)</script>\n'+doc
        p=truth['proposal'];p['rules'][0]['quote']='Invented sentence.'
        row=review(doc,p,lambda item:True);page=render(row)
        self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)
        self.assertIn('couldn&#x27;t convert',page);self.assertIn('Invented sentence.',page)
        self.assertIn('Fake Spark response',page);self.assertNotIn('<form',page)
    def test_confirmed_file_runs_in_separate_checker_adapter(self):
        from spec_guard.run import run_confirmed
        from spec_guard.view import save
        doc,truth=fixture('shipping');row=review(doc,truth['proposal'],lambda item:True)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);save(row,root/'spec')
            candidate=root/'solution.py';candidate.write_text('def solve(x):\n return "express" if x["express"] and not x["hazardous"] else "ground"\n')
            checked=run_confirmed(root/'spec/confirmed.yaml',candidate=candidate,out=root/'checked')
            self.assertEqual(checked['outcome'],'PASS');self.assertFalse(checked['model_invoked'])
            self.assertEqual({r['layer'] for r in checked['tests']},{'visible','hidden'})
    def test_conflicted_spec_stops_before_any_model(self):
        from unittest.mock import patch
        from spec_guard.run import run_confirmed
        from spec_guard.view import save
        doc,truth=fixture();row=review(doc,truth['proposal'],lambda item:True)
        with tempfile.TemporaryDirectory() as directory,patch('spec_guard.run.budgeted') as paid:
            root=Path(directory);save(row,root/'spec')
            checked=run_confirmed(root/'spec/confirmed.yaml',real=True,out=root/'checked')
            self.assertEqual(checked['outcome'],'CONFLICT VERIFIED');paid.assert_not_called()
    def test_live_date_gate_prevents_today_before_key_or_network(self):
        from unittest.mock import patch
        from spec_guard.provider import propose
        with patch('spec_guard.provider.today',return_value='2026-10-26'),patch('spec_guard.provider.Gateway') as gateway:
            with self.assertRaisesRegex(ValueError,'No paid calls today'):propose('a doc')
            gateway.assert_not_called()
    def test_fake_transport_records_actual_usage_without_real_provider(self):
        import os
        from unittest.mock import patch
        from muse_guard.gateway import Gateway
        from spec_guard.provider import propose
        doc,truth=fixture();calls=[]
        def transport(path,data):
            calls.append((path,data))
            if path.endswith('input_tokens'):return {'input_tokens':100}
            return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(truth['proposal'])}]}],
                    'usage':{'input_tokens':100,'output_tokens':100,'input_tokens_details':{'cached_tokens':0}}}
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'META_API_KEY':'planted-key'}),patch('spec_guard.provider.RESULTS',Path(directory)),patch('spec_guard.provider.today',return_value='2026-10-27'),patch('spec_guard.provider.Gateway',side_effect=lambda key,**kwargs:Gateway(key,transport=transport,**kwargs)):
            proposal,cost=propose(doc)
            self.assertEqual(proposal,truth['proposal']);self.assertAlmostEqual(cost['cost_usd'],0.00055)
            self.assertEqual(cost['provider_calls'],1);self.assertEqual(calls[-1][1]['input'],doc)
            ledger=json.loads((Path(directory)/'total.json').read_text());self.assertAlmostEqual(ledger['known_cost_usd'],0.00055)
    def test_shared_cap_and_unknown_receipt_stop_before_network(self):
        import os
        from unittest.mock import patch
        from spec_guard.provider import propose
        for cost in (5,None):
            with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'META_API_KEY':'planted-key'}),patch('spec_guard.provider.RESULTS',Path(directory)),patch('spec_guard.provider.today',return_value='2026-10-27'),patch('spec_guard.provider.Gateway') as gateway:
                (Path(directory)/'prior.json').write_text(json.dumps({'run_id':'prior','date':'2026-10-27','cost_usd':cost}))
                with self.assertRaises(ValueError):propose('doc')
                gateway.assert_not_called()

    def test_fake_evaluation_is_complete_and_explicitly_not_model_results(self):
        from unittest.mock import patch
        from spec_guard.evaluation import evaluate
        with tempfile.TemporaryDirectory() as directory,patch('spec_guard.evaluation.propose') as paid:
            report=evaluate(Path(directory)/'evaluation')
            paid.assert_not_called()
            self.assertEqual(report['status'],'COMPLETE')
            self.assertIn('FAKE',report['kind'])
            self.assertEqual(report['totals']['rules_correctly_extracted'],24)
            self.assertEqual(report['totals']['clashes_found'],5)
            self.assertEqual(report['totals']['successful_documents'],8)
            self.assertEqual(report['completed_call_cost_usd'],0)
    def test_manifest_rejects_modified_corpus(self):
        from unittest.mock import patch
        from spec_guard.evaluation import verify_manifest
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'doc.md').write_text('changed')
            (root/'MANIFEST.json').write_text(json.dumps({'files':{'doc.md':'0'*64}}))
            with patch('spec_guard.evaluation.ROOT',root),patch('spec_guard.evaluation.CORPUS',root):
                with self.assertRaisesRegex(ValueError,'preregistration drift'):verify_manifest()
    def test_nonfinite_model_response_is_retained_as_invalid(self):
        from spec_guard.view import render
        doc,truth=fixture();truth['proposal']['input_space']['eligible']=[float('nan')]
        row=review(doc,truth['proposal'],lambda item:True)
        self.assertTrue(row['validation']['errors'])
        self.assertEqual(row['confirmed']['rules'],[])
        self.assertIn('No clashes',render(row))

    def test_interactive_review_confirms_and_rejects_explicitly(self):
        import io
        from unittest.mock import patch
        from spec_guard.cli import decision
        item={'proposal':{'quote':'A source sentence.','when':{'flag':{'eq':True}},'action':'allow'}}
        with patch('builtins.input',side_effect=['maybe','y','n']),patch('sys.stdout',new_callable=io.StringIO) as output:
            self.assertTrue(decision(item));self.assertFalse(decision(item))
            self.assertIn('A source sentence.',output.getvalue())
            self.assertIn('Enter y',output.getvalue())
    def test_missing_usage_retains_reservation_and_blocks_next_call(self):
        import os
        from unittest.mock import patch
        from muse_guard.gateway import Gateway
        from spec_guard.provider import propose
        def transport(path,data):
            if path.endswith('input_tokens'):return {'input_tokens':100}
            return {'status':'completed','output':[]}
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'META_API_KEY':'planted-key'}),patch('spec_guard.provider.RESULTS',Path(directory)),patch('spec_guard.provider.today',return_value='2026-10-27'),patch('spec_guard.provider.Gateway',side_effect=lambda key,**kwargs:Gateway(key,transport=transport,**kwargs)) as gateway:
            with self.assertRaises(ValueError):propose('doc')
            receipts=list(Path(directory).glob('spec-extract-*.json'));self.assertEqual(len(receipts),1)
            receipt=json.loads(receipts[0].read_text());self.assertIsNone(receipt['cost_usd'])
            self.assertGreater(receipt['accounted_upper_bound_usd'],0)
            with self.assertRaisesRegex(ValueError,'unknown'):propose('doc')
            self.assertEqual(gateway.call_count,1)
