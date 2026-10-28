"""Existing service contract. Checker reuses a pristine copy, never agent edits."""
import http.client
import json
import threading
import unittest

CLIENT=None


class LocalClient:
    def __init__(self,port):self.port=port
    def request(self,method,path,body=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.port,timeout=2)
        data=None if body is None else json.dumps(body)
        try:
            connection.request(method,path,body=data,headers={'Content-Type':'application/json'})
            response=connection.getresponse()
            return response.status,json.loads(response.read())
        finally:connection.close()


class ExistingService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global CLIENT
        cls.owned=CLIENT is None
        if cls.owned:
            from server import make_server
            cls.server=make_server()
            cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
            cls.client=LocalClient(cls.server.server_port)
        else:cls.client=CLIENT
    @classmethod
    def tearDownClass(cls):
        if cls.owned:cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def new(self,**changes):
        return self.client.request('POST','/returns',dict(eligible=True,fraud_hold=False,amount_cents=2500,**changes))
    def test_health(self):
        self.assertEqual(self.client.request('GET','/health'),(200,{'status':'ok','service':'returns-demo'}))
    def test_create_and_get(self):
        data={'eligible':True,'fraud_hold':False,'amount_cents':2500}
        status,row=self.client.request('POST','/returns',data);self.assertEqual(status,201)
        self.assertEqual({k:row[k] for k in data},data);self.assertEqual(row['next_action'],'not_evaluated')
        self.assertRegex(row['id'],r'^r[1-9][0-9]*$')
        self.assertEqual(self.client.request('GET','/returns/'+row['id']),(200,row))
    def test_unique_ids(self):
        a=self.new()[1];b=self.new()[1];self.assertNotEqual(a['id'],b['id'])
    def test_invalid_fields(self):
        for data in ({},{'eligible':True,'fraud_hold':False,'amount_cents':True},
                     {'eligible':'yes','fraud_hold':False,'amount_cents':2500},
                     {'eligible':True,'fraud_hold':False,'amount_cents':-1},
                     {'eligible':True,'fraud_hold':False,'amount_cents':2500,'extra':1}):
            with self.subTest(data=data):self.assertEqual(self.client.request('POST','/returns',data)[0],400)
    def test_unknown_routes(self):
        for method,path in [('GET','/missing'),('GET','/returns/r999999'),('POST','/returns/r999999/evaluate')]:
            with self.subTest(path=path):self.assertEqual(self.client.request(method,path),(404,{'error':'not_found'}))
    def test_evaluation_persists(self):
        row=self.new()[1];path='/returns/'+row['id']
        status,evaluated=self.client.request('POST',path+'/evaluate',{})
        self.assertEqual(status,200);self.assertIn(evaluated['next_action'],('refund_immediately','manual_review','reject'))
        self.assertEqual(self.client.request('GET',path),(200,evaluated))
        self.assertEqual(evaluated['amount_cents'],2500)
    def test_evaluate_rejects_payload(self):
        row=self.new()[1]
        self.assertEqual(self.client.request('POST','/returns/'+row['id']+'/evaluate',{'unexpected':True})[0],400)
