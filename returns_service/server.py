"""Tiny in-memory returns service. No payments or external integrations."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import socket
from refund_policy import next_action


class Handler(BaseHTTPRequestHandler):
    server_version='ReturnsDemo/0.1'
    def log_message(self,*args):pass
    def reply(self,status,body):
        payload=json.dumps(body,separators=(',',':')).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)
    def body(self,empty=False):
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<=length<=4096:raise ValueError()
            if not length and empty:return {}
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError()
            return data
        except (ValueError,UnicodeError):raise ValueError('Invalid JSON object') from None
    def do_GET(self):
        if self.path=='/health':return self.reply(200,{'status':'ok','service':'returns-demo'})
        match=re.fullmatch(r'/returns/(r[1-9][0-9]*)',self.path)
        row=self.server.records.get(match[1]) if match else None
        if row is None:return self.reply(404,{'error':'not_found'})
        self.reply(200,row)
    def do_POST(self):
        if self.path=='/returns':
            try:
                row=self.body()
                if (set(row)!={'eligible','fraud_hold','amount_cents'} or
                    type(row['eligible']) is not bool or type(row['fraud_hold']) is not bool or
                    type(row['amount_cents']) is not int or not 0<=row['amount_cents']<=1000000):raise ValueError()
            except ValueError:return self.reply(400,{'error':'invalid_request'})
            identity='r'+str(self.server.next_id);self.server.next_id+=1
            saved=dict(row,id=identity,next_action='not_evaluated')
            self.server.records[identity]=saved
            return self.reply(201,saved)
        match=re.fullmatch(r'/returns/(r[1-9][0-9]*)/evaluate',self.path)
        row=self.server.records.get(match[1]) if match else None
        if row is None:return self.reply(404,{'error':'not_found'})
        try:
            if self.body(empty=True)!={}:raise ValueError()
        except ValueError:return self.reply(400,{'error':'invalid_request'})
        row['next_action']=next_action(row)
        if row['next_action'] not in ('refund_immediately','manual_review','reject'):
            return self.reply(500,{'error':'invalid_policy_action'})
        self.reply(200,row)


def make_server(port=0,fd=None):
    server=HTTPServer(('127.0.0.1',port),Handler,bind_and_activate=fd is None)
    if fd is not None:
        server.socket.close()
        server.socket=socket.socket(fileno=fd)
        server.server_address=server.socket.getsockname()
        server.server_name='127.0.0.1';server.server_port=server.server_address[1]
    server.records={};server.next_id=1
    return server


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8001)
    parser.add_argument('--socket-fd',type=int);args=parser.parse_args()
    server=make_server(args.port,args.socket_fd)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
