"""Local saved-evidence display. Verdicts are read from the independent run record."""
import difflib
from html import escape
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import webbrowser

from .recovery import frozen_solution,resume_recovery

ASSETS=Path(__file__).with_name("view_assets")


def text(value):
    return escape(str(value),quote=True)


def load_record(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>4*1024*1024:
        raise ValueError("Run record unavailable or too large")
    row=json.loads(path.read_text())
    if not isinstance(row,dict) or not (row.get("run_id") or row.get("recovery_id")):
        raise ValueError("Choose a run JSON record")
    return row


def repair_diff(row,results):
    if isinstance(row.get("repair_diff"),str):return row["repair_diff"]
    try:
        before=frozen_solution(results,row["attempt"]).decode()
        after=frozen_solution(results,row["repair"]).decode()
        return "".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="before/solution.py",tofile="after/solution.py")) or "No solution changes recorded."
    except (KeyError,OSError,ValueError,UnicodeError):
        return "Repair diff unavailable: frozen artifacts are missing or failed their recorded hashes."


def display_requirements(row):
    """Use recorded public rules, or the exact hash-matching historical catalog entry."""
    if row.get('requirements_v1'):return row['requirements_v1']
    from .rules import TASKS,digest
    for task in TASKS.values():
        if task['id']==row.get('task') and digest(task['requirements'])==row.get('requirements_hash'):
            return task['requirements']
    return {}


def render(row,*,diff_text="Repair diff unavailable for this record.",live=False,token=""):
    req=display_requirements(row)
    proof=row.get("conflict_validation",row.get("attempt",{}).get("conflict_validation",{}))
    verified=proof.get("verified") is True
    ids=proof.get("rules",[]) if verified else []
    rules="".join('<tr class="'+('clash' if rule.get('id') in ids else '')+'"><th scope="row">Rule '+text(rule.get('id','?'))+'</th><td>'+text(rule.get('text',''))+'</td><td><code>'+text(rule.get('action',''))+'</code></td></tr>' for rule in req.get('rules',[]))
    witness=proof.get('witness',row.get('witness'))
    demands="".join('<li><strong>Rule '+text(key)+'</strong> requires <code>'+text(action)+'</code></li>' for key,action in zip(proof.get('rules',[]),proof.get('actions',[]))) if verified else ''
    card=row.get('conflict_card',{}).get('text','No conflict card recorded.')
    final=row.get('repair',row.get('attempt',row))
    checks=final.get('tests',[]);passed=sum(check.get('status')=='PASS' for check in checks)
    check_rows=''.join('<tr><td>'+text(check.get('layer','unspecified'))+'</td><th scope="row">'+text(check.get('id','unknown'))+'</th><td class="'+('pass' if check.get('status')=='PASS' else 'fail')+'">'+text(check.get('status','UNKNOWN'))+'</td></tr>' for check in checks)
    diff='\n'.join('<span class="'+('add' if line.startswith('+') and not line.startswith('+++') else 'remove' if line.startswith('-') and not line.startswith('---') else '')+'">'+text(line)+'</span>' for line in diff_text.splitlines())
    active=live and row.get('status')=='AWAITING DECISION' and verified
    winner=row.get('decision',{}).get('winner')
    buttons=''.join('<button type="button" data-winner="'+key+'"'+('' if active else ' disabled')+'>Rule '+key+' wins</button>' for key in ('A','B'))
    status=row.get('status',row.get('outcome','UNKNOWN'));verdict=final.get('outcome','Pending recheck')
    cost='Unknown' if row.get('cost_usd') is None else '$'+format(row['cost_usd'],'.5f')
    values={
        'context':('A requirements conflict, resolved with one decision' if row.get('status')=='RECOVERED' else 'Independent evidence from a Muse Code attempt'),
        'title':text(row.get('task','Run evidence')),'mode':'Live decision' if live else 'Recorded run',
        'rules':rules or '<tr><td>No rules table in this record.</td></tr>',
        'badge':'<span class="badge">Verified by checker</span>' if verified else '<span class="pending">No verified witness recorded</span>',
        'witness':text(json.dumps(witness,indent=2) if witness is not None else 'No witness recorded.'),
        'demands':demands,'card':text(card),'buttons':buttons,
        'decision_note':text(('Choose which rule takes precedence. This starts the real repair.' if active else 'Recorded choice: Rule '+winner+' wins.' if winner else 'Replay is read-only.' if not live else 'Decision submitted; see the run status.')),
        'diff':diff,'checks':check_rows or '<tr><td>No independent checks recorded yet.</td></tr>',
        'count':str(passed)+' / '+str(len(checks)), 'verdict':text(verdict),'status':text(status),
        'cost':cost,'token':text(token),'run_id':text(row.get('recovery_id',row.get('run_id',''))),
    }
    page=(ASSETS/'index.html').read_text()
    for key,value in values.items():page=page.replace('@@'+key+'@@',value)
    return page


def create_server(record_path,*,live=False,env=None,port=0):
    record_path=Path(record_path).expanduser()
    initial=load_record(record_path)
    if live:
        from .recovery import RESULTS_ROOT
        if record_path.resolve().parent!=RESULTS_ROOT.resolve():
            raise ValueError("Live view requires the canonical repository results ledger")
        from .rules import TASKS,verify_conflict,digest
        task=TASKS.get(initial.get('task'))
        if (initial.get('status')!='AWAITING DECISION' or initial.get('study_holdout') or not task or
            digest(initial.get('requirements_v1'))!=digest(task['requirements']) or
            not verify_conflict(task['requirements'],initial.get('conflict_report'))['verified']):
            raise ValueError('Live view requires a verified paused development recovery')
        frozen_solution(record_path.parent,initial['attempt'])
    token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body,kind):
            self.send_response(status)
            self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers();self.wfile.write(body)
        def allowed_host(self):return self.headers.get('Host')=='127.0.0.1:'+str(self.server.server_port)
        def do_GET(self):
            if not self.allowed_host():return self.send(403,b'Forbidden host','text/plain')
            if self.path=='/':
                row=load_record(record_path)
                return self.send(200,render(row,diff_text=repair_diff(row,record_path.parent),live=live,token=token if live else '').encode(),'text/html; charset=utf-8')
            if self.path=='/evidence.json':
                return self.send(200,record_path.read_bytes(),'application/json')
            if self.path in ('/style.css','/view.js'):
                return self.send(200,(ASSETS/self.path[1:]).read_bytes(),'text/css' if self.path.endswith('.css') else 'text/javascript')
            self.send(404,b'Not found','text/plain')
        def do_POST(self):
            origin='http://127.0.0.1:'+str(self.server.server_port)
            if (not live or self.path!='/decision' or not self.allowed_host() or
                self.headers.get('Origin')!=origin or self.headers.get('X-Decision-Token')!=token or
                self.headers.get('Content-Type')!='application/json'):
                return self.send(403,b'Forbidden','text/plain')
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=128:raise ValueError('Invalid request size')
                packet=json.loads(self.rfile.read(size));winner=packet.get('winner')
                if winner not in ('A','B'):raise ValueError('Choose A or B')
                row=resume_recovery(record_path,winner,env=env)
                self.send(200,json.dumps({'status':row['status']}).encode(),'application/json')
            except (ValueError,OSError,KeyError,TypeError):self.send(409,b'Decision refused; inspect the run record.','text/plain')
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def serve(record_path,*,live=False,port=0,open_browser=True):
    server=create_server(record_path,live=live,port=port)
    url='http://127.0.0.1:'+str(server.server_port)
    print(url+'  ('+('live decision' if live else 'recorded run')+')',flush=True)
    if open_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
