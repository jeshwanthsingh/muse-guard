"""Offline protocol and budget fixtures; these tests make no paid provider calls."""
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

from muse_guard.checker import _observe, ObservationError
from muse_guard.gateway import TokenBudget, Gateway
from muse_guard.runner import reserve_budget


class FollowupTests(unittest.TestCase):
    def test_token_limit_reserves_input_and_output_before_call(self):
        budget = TokenBudget(100)
        self.assertEqual(budget.admit(30, 40), 40)
        with self.assertRaises(ValueError):
            budget.admit(31, 1)
        self.assertEqual(budget.reserved_tokens, 70)

    def test_output_limit_cannot_exceed_remaining_tokens(self):
        budget = TokenBudget(100)
        self.assertEqual(budget.admit(60, 128000), 40)
        with self.assertRaises(ValueError):
            budget.admit(1, 1)

    def test_daily_cap_reserves_worst_case_next_run(self):
        with self.assertRaises(ValueError):
            reserve_budget([{"cost_usd":4.8}], 0.68)
        self.assertEqual(reserve_budget([{"cost_usd":4.2}], 0.68), 0.68)

    def test_unknown_or_bad_token_counts_never_launch(self):
        for value in (None, -1, True, 1.2):
            with self.assertRaises(ValueError):
                TokenBudget(100).admit(value, 10)

    def test_sandbox_allows_only_own_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            candidate=root/'solution.py'
            forbidden=root/'outside.txt'
            candidate.write_text("from pathlib import Path\ndef solve(x):\n Path('inside.txt').write_text('allowed')\n try:\n  Path("+repr(str(forbidden))+").write_text('forbidden')\n except PermissionError:\n  return x\n return 99\n")
            self.assertEqual(_observe(candidate, 3), 3)
            self.assertFalse(forbidden.exists())

    def test_sandbox_blocks_live_local_network_connection(self):
        with socket.socket() as server, tempfile.TemporaryDirectory() as directory:
            server.bind(('127.0.0.1',0));server.listen()
            root=Path(directory); candidate=root/'solution.py'
            port=server.getsockname()[1]
            candidate.write_text("import socket\ndef solve(x):\n try:\n  socket.create_connection(('127.0.0.1',"+str(port)+"),timeout=0.2)\n except PermissionError:\n  return x\n return 99\n")
            self.assertEqual(_observe(candidate, 3), 3)

    def test_gateway_forces_standard_and_clamps_generation(self):
        calls=[]
        def transport(path, data):
            calls.append((path,data))
            if path.endswith('input_tokens'):
                return {'input_tokens':30}
            return {'usage':{'input_tokens':30,'output_tokens':1}}
        with Gateway('fixture',token_limit=100, transport=transport) as gateway:
            import urllib.request
            data={'model':'muse-spark-1.3-contributor','input':'hello','max_output_tokens':128000}
            request=urllib.request.Request(gateway.url+'/responses', data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request) as response:
                self.assertEqual(response.status,200)
        self.assertEqual(calls[-1][1]['model'],'muse-spark-1.3')
        self.assertEqual(calls[-1][1]['max_output_tokens'],70)
        self.assertEqual(gateway.budget.reserved_tokens,100)

    def test_runner_refuses_next_run_when_reservation_would_exceed_five(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from muse_guard.runner import run_one
        from muse_guard.legacy_tasks import TASKS
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            day=datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
            (root/'prior.json').write_text(json.dumps({'run_id':'prior','date':day,'cost_usd':4.8}))
            row=run_one(TASKS['identity-solvable'],root,env={'META_API_KEY':'fixture'})
            self.assertFalse(row['model_invoked'])
            self.assertEqual(row['outcome'],'HARNESS ERROR')
            self.assertIn('$5',row['reason'])

    def test_gateway_rejects_uncounted_conversation_context(self):
        import urllib.request, urllib.error
        calls=[]
        def transport(path,data):
            calls.append(path)
            return {'input_tokens':1}
        with Gateway('fixture',transport=transport) as gateway:
            request=urllib.request.Request(gateway.url+'/responses',data=json.dumps({'model':'muse-spark-1.3','input':'x','conversation':'old-context'}).encode(),headers={'Content-Type':'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(request)
            caught.exception.close()
        self.assertEqual(calls,[])

    def test_shutdown_waits_for_active_requests_before_accounting(self):
        import threading, time, urllib.request
        started=threading.Event(); release=threading.Event(); calls=[]
        def transport(path,data):
            calls.append(path)
            if path.endswith('input_tokens'):
                started.set(); release.wait(2)
                return {'input_tokens':1}
            return {'usage':{'input_tokens':1,'output_tokens':1}}
        with Gateway('fixture',transport=transport) as gateway:
            def request():
                try:
                    urllib.request.urlopen(urllib.request.Request(gateway.url+'/responses',data=b'{"input":"x"}',headers={'Content-Type':'application/json'})).close()
                except urllib.error.HTTPError as error:
                    error.close()
                except Exception:
                    pass
            client=threading.Thread(target=request);client.start()
            self.assertTrue(started.wait(1))
            stopper=threading.Thread(target=gateway.stop);stopper.start()
            time.sleep(0.05)
            self.assertTrue(stopper.is_alive())
            release.set();stopper.join(2);client.join(2)
            self.assertFalse(stopper.is_alive())
        self.assertEqual(calls,['/responses/input_tokens'])

    def test_unresolved_crashed_run_blocks_restart(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from muse_guard.runner import run_one
        from muse_guard.legacy_tasks import TASKS
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            day=datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
            (root/'pending.json').write_text(json.dumps({'run_id':'pending','date':day,'cost_usd':None,'reserved_cost_usd':0.68}))
            row=run_one(TASKS['identity-solvable'],root,env={'META_API_KEY':'fixture'})
            self.assertFalse(row['model_invoked'])
            self.assertIn('Unknown usage',row['reason'])

    def test_gateway_accepts_only_function_namespaces(self):
        import urllib.request, urllib.error
        calls=[]
        def transport(path,data):
            calls.append(path)
            return {'input_tokens':1} if path.endswith('input_tokens') else {'usage':{'input_tokens':1,'output_tokens':1}}
        with Gateway('fixture',transport=transport) as gateway:
            def request(kind):
                data={'input':'x','tools':[{'type':'namespace','name':'muse','tools':[{'type':kind,'name':'bash'}]}]}
                return urllib.request.urlopen(urllib.request.Request(gateway.url+'/responses',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'}))
            with request('function') as response:
                self.assertEqual(response.status,200)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                request('web_search')
            caught.exception.close()
        self.assertEqual(calls,['/responses/input_tokens','/responses'])

    def test_streamed_provider_usage_covers_ephemeral_reminders(self):
        from muse_guard.gateway import response_usage
        body=b'data: {"type":"response.completed","response":{"usage":{"input_tokens":20,"output_tokens":3,"input_tokens_details":{"cached_tokens":10}}}}\n\n'
        self.assertEqual(response_usage(body),{'input_tokens':20,'output_tokens':3,'cached_input_tokens':10})
        self.assertIsNone(response_usage(b'data: [DONE]\n'))

    def test_partial_stream_or_invalid_request_usage_is_unknown(self):
        from muse_guard.gateway import response_usage
        packets=[
            {'type':'response.in_progress','response':{'usage':{'input_tokens':1,'output_tokens':1}}},
            {'type':'response.completed','response':{'usage':{'input_tokens':-1,'output_tokens':1}}},
            {'type':'response.completed','response':{'usage':{'input_tokens':1,'output_tokens':1,'input_tokens_details':{'cached_tokens':2}}}},
        ]
        for packet in packets:
            self.assertIsNone(response_usage(('data: '+json.dumps(packet)+'\n').encode()))
        self.assertIsNone(response_usage(b'{"status":"in_progress","usage":{"input_tokens":1,"output_tokens":1}}'))

    def test_retained_reservation_counts_toward_daily_cap(self):
        self.assertEqual(reserve_budget([{'cost_usd':None,'accounted_upper_bound_usd':0.68}],0.68),0.68)
        with self.assertRaises(ValueError):
            reserve_budget([{'cost_usd':4.2},{'cost_usd':None,'accounted_upper_bound_usd':0.68}],0.68)

    def test_negative_cost_cannot_cancel_other_spend(self):
        with self.assertRaises(ValueError):
            reserve_budget([{'cost_usd':-1},{'cost_usd':1}],0.68)
