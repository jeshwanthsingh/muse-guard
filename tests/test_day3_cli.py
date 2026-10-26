import unittest
from muse_guard.recovery import choose_decision
from muse_guard.cli import evidence
from pathlib import Path

class DecisionTests(unittest.TestCase):
 def test_interactive_choice_retries_invalid_input(self):
  replies=iter(['wrong','B'])
  self.assertEqual(choose_decision(['A','B'],input_fn=lambda _:next(replies)),('B','interactive developer CLI'))
 def test_scripted_choice_and_no_approval_on_empty(self):
  self.assertEqual(choose_decision(['A','B'],'A'),('A','scripted developer CLI'))
  self.assertEqual(choose_decision(['A','B'],input_fn=lambda _:''),(None,None))
  with self.assertRaises(ValueError):choose_decision(['A','B'],'C')
 def test_evidence_summary_has_checker_and_cost(self):
  text=evidence({'run_id':'fixture','outcome':'PASS','cost_usd':0.01,'tests':[{'status':'PASS'}]},Path('results'))
  self.assertIn('checks 1/1',text);self.assertIn('$0.01000000',text)


class CancelledReminderTests(unittest.TestCase):
 def test_disconnected_client_keeps_usage_without_policy_failure(self):
  import socket,struct,threading,tempfile,json
  from muse_guard.gateway import Gateway
  started=threading.Event();release=threading.Event()
  def transport(path,data):
   if path.endswith('input_tokens'):return {'input_tokens':1}
   started.set();release.wait(2)
   return {'status':'completed','usage':{'input_tokens':1,'output_tokens':1}}
  with tempfile.TemporaryDirectory() as directory:
   journal=Path(directory)/'usage.json'
   with Gateway('fixture',transport=transport,journal=journal) as gateway:
    port=int(gateway.url.rsplit(':',1)[1])
    client=socket.create_connection(('127.0.0.1',port))
    body=b'{"input":"toy"}'
    client.sendall(b'POST /responses HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body)
    self.assertTrue(started.wait(1))
    client.setsockopt(socket.SOL_SOCKET,socket.SO_LINGER,struct.pack('ii',1,0));client.close();release.set()
   events=json.loads(journal.read_text())['requests']
   self.assertEqual(len(events),1)
   self.assertEqual(events[0]['usage']['output_tokens'],1)


class RealDecisionReceiptTests(unittest.TestCase):
 def test_interactive_decision_is_bound_and_not_marked_simulated(self):
  from muse_guard.rules import TASKS,approve,approved
  req=TASKS['refund-impossible']['requirements']
  report={'conflict':True,'rules':['A','B'],'witness':{'eligible':True,'fraud_hold':True,'context':'card'},'explanation':'clash'}
  v2=approve(req,'B',report,confirmed=True,source='interactive developer CLI')
  self.assertTrue(approved(v2));self.assertFalse(v2['decision']['simulated'])
  self.assertEqual(v2['decision']['source'],'interactive developer CLI')
