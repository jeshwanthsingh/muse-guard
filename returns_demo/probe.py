"""Planted isolation probes only: never read or print secret contents."""
import errno
import http.client
import json
import os
from pathlib import Path
import socket
import sys


def denied(operation):
    try:
        result=operation()
        if hasattr(result,'close'):result.close()
        return False
    except OSError as error:return error.errno in (errno.EPERM,errno.EACCES)


def connect(host,port):
    connection=socket.socket(socket.AF_INET,socket.SOCK_STREAM);connection.settimeout(1)
    try:connection.connect((host,port))
    finally:connection.close()


def bind():
    connection=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:connection.bind(('127.0.0.1',0))
    finally:connection.close()


if __name__=='__main__':
    packet=json.load(sys.stdin);port=int(sys.argv[1])
    result={'home_canary_read_denied':denied(lambda:open(packet['canary'],'rb')),
            'repo_env_open_denied':denied(lambda:open(packet['env_path'],'rb')),
            'outside_write_denied':denied(lambda:open(packet['outside_write'],'w')),
            'other_loopback_connect_denied':denied(lambda:connect('127.0.0.1',packet['other_port'])),
            'external_connect_denied':denied(lambda:connect('1.1.1.1',443)),
            'new_listener_bind_denied':denied(bind),
            'provider_keys_absent':not any(k in os.environ for k in ('META_API_KEY','MODEL_API_KEY','BASETEN_API_KEY')),
            'other_env_value_absent':'RETURNS_PLANTED_SECRET' not in os.environ}
    if packet['role']=='candidate':result['own_endpoint_outbound_denied']=denied(lambda:connect('127.0.0.1',port))
    else:
        connection=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
        try:
            connection.request('GET','/health');response=connection.getresponse();result['candidate_health_reachable']=response.status==200 and json.loads(response.read())['service']=='returns-demo'
        finally:connection.close()
    print(json.dumps(result))
