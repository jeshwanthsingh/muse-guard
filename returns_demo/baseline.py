"""Record actual local baseline HTTP traffic. No agent or provider is invoked."""
import hashlib
import importlib.util
import json
from pathlib import Path
import threading

ROOT=Path(__file__).resolve().parents[1]


def record():
    import sys
    sys.path.insert(0,str(ROOT/'returns_service'))
    from server import make_server
    from test_existing import LocalClient
    server=make_server();thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    rows=[]
    try:
        client=LocalClient(server.server_port)
        for fraud_hold in (True,False):
            request={'eligible':True,'fraud_hold':fraud_hold,'amount_cents':2500}
            status,body=client.request('POST','/returns',request)
            rows.append({'request':{'method':'POST','path':'/returns','json':request},'response':{'status':status,'json':body}})
            path='/returns/'+body['id']+'/evaluate';status,body=client.request('POST',path,{})
            rows.append({'request':{'method':'POST','path':path,'json':{}},'response':{'status':status,'json':body}})
        return {'kind':'actual baseline HTTP traffic; no model call','cost_usd':0,'requests':rows,
                'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'returns_service').glob('*.py')}}
    finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':
    print(json.dumps(record(),indent=2))
