"""Trusted HTTP checks, executed separately from candidate code and its folder."""
import http.client
import json
import re
import sys
import time
import unittest


class EndpointClient:
    def __init__(self,port):self.port=port;self.requests=[];self.current='startup'
    def request(self,method,path,body=None):
        if method not in ('GET','POST') or not re.fullmatch(r'/(?:health|returns(?:/r[1-9][0-9]*(?:/evaluate)?)?)',path):
            # The unknown-route regression uses this fixed local path too.
            if path!='/missing' or method!='GET':raise ValueError('Endpoint-relative path required')
        connection=http.client.HTTPConnection('127.0.0.1',self.port,timeout=2)
        data=None if body is None else json.dumps(body)
        row={'check':self.current,'request':{'method':method,'path':path,'json':body}}
        try:
            connection.request(method,path,body=data,headers={'Content-Type':'application/json'})
            response=connection.getresponse();raw=response.read(65537)
            if len(raw)>65536:raise ValueError('Response too large')
            if response.getheader('Content-Type','').split(';')[0]!='application/json':raise ValueError('JSON response required')
            packet=json.loads(raw)
            row['response']={'status':response.status,'json':packet};self.requests.append(row)
            # HTTPConnection does not follow redirects; there is no URL option.
            return response.status,packet
        finally:connection.close()


class Results(unittest.TestResult):
    def __init__(self,client):super().__init__();self.rows=[];self.client=client;self.states={}
    def identity(self,test):return 'policy.'+test._testMethodName if type(test).__name__=='ApprovedPolicy' else 'regression.'+test._testMethodName
    def startTest(self,test):super().startTest(test);self.client.current=self.identity(test)
    def addSuccess(self,test):super().addSuccess(test);self.states.setdefault(self.identity(test),{'status':'PASS'})
    def addFailure(self,test,err):super().addFailure(test,err);self.states[self.identity(test)]={'status':'FAIL','reason':str(err[1])[:512]}
    def addError(self,test,err):super().addError(test,err);self.states[self.identity(test)]={'status':'ERROR','reason':type(err[1]).__name__}
    def addSkip(self,test,reason):super().addSkip(test,reason);self.states[self.identity(test)]={'status':'SKIP'}
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err:self.states[self.identity(test)]={'status':'FAIL','reason':'Existing contract subtest failed'}
    def stopTest(self,test):
        self.rows.append(dict(id=self.identity(test),**self.states.get(self.identity(test),{'status':'ERROR'})))
        super().stopTest(test)


def run(port,packet):
    import test_existing
    client=EndpointClient(port)
    ready=False
    for _ in range(40):
        try:
            if client.request('GET','/health')==(200,{'status':'ok','service':'returns-demo'}):ready=True;break
        except (OSError,ValueError,http.client.HTTPException):pass
        time.sleep(.05)
    if not ready:return {'outcome':'HARNESS ERROR','reason':'Candidate HTTP service did not become ready','tests':[],'http':client.requests}
    methods={}
    for index,case in enumerate(packet['cases']):
        def check(self,case=case):
            payload=dict(case['input'],amount_cents=2500)
            status,row=client.request('POST','/returns',payload);self.assertEqual(status,201)
            self.assertEqual({k:row[k] for k in payload},payload)
            status,observed=client.request('POST','/returns/'+row['id']+'/evaluate',{})
            self.assertEqual(status,200);self.assertEqual(observed['next_action'],case['expected'])
            self.assertEqual(client.request('GET','/returns/'+row['id']),(200,observed))
        methods['test_case_'+str(index)]=check
    policy=type('ApprovedPolicy',(unittest.TestCase,),methods)
    test_existing.CLIENT=client
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(policy),unittest.defaultTestLoader.loadTestsFromTestCase(test_existing.ExistingService)])
    result=Results(client);suite.run(result)
    ids=[r['id'] for r in result.rows]
    complete=(len(ids)==len(set(ids)) and set(ids)==set(packet['expected_test_ids']) and all(r['status'] in ('PASS','FAIL','ERROR') for r in result.rows))
    return {'outcome':'PASS' if complete and all(r['status']=='PASS' for r in result.rows) else 'FAIL' if complete else 'HARNESS ERROR',
            'tests':result.rows,'inventory_complete':complete,'http':client.requests}


if __name__=='__main__':
    try:result=run(int(sys.argv[1]),json.load(sys.stdin))
    except (ValueError,OSError,KeyError,TypeError):result={'outcome':'HARNESS ERROR','reason':'Trusted checker input or transport failed','tests':[],'http':[]}
    print(json.dumps(result))
