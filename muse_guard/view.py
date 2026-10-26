"""Local saved-evidence display. Verdicts are read from the independent run record."""
import difflib
import hashlib
from html import escape
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import re
import webbrowser

from .recovery import frozen_solution,resume_recovery

ASSETS=Path(__file__).with_name("view_assets")


def text(value):
    return escape(str(value),quote=True)


def inline_code(value):
    parts=re.split(r'(`[^`\n]+`)',value)
    return ''.join('<code>'+text(part[1:-1])+'</code>' if len(part)>2 and part.startswith('`') and part.endswith('`') else text(part) for part in parts)


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


TITLES={'retry':'HTTP retry policy','refund':'Refund policy','shipping':'Shipping policy','access':'Access policy',
        'discount':'Discount policy','pricing':'Pricing policy','rate-limit':'Rate-limit policy','feature':'Feature flags',
        'notification':'Notification policy','retention':'Data retention policy'}


def progress(row):
    attempt=row.get('attempt',row);repair=row.get('repair',{})
    report=attempt.get('conflict_report',{})
    final=repair or attempt
    done=[bool(attempt.get('model_invoked')),report.get('conflict') is True,bool(row.get('decision')),
          bool(repair.get('model_invoked')),bool(final.get('tests')) and final.get('outcome')!='HARNESS ERROR']
    labels=[('attempt','Attempt'),('conflict','Conflict found'),('decision','You decide'),('repair','Repair'),('checked','Checked')]
    return ''.join('<li class="step '+('complete' if complete else 'pending')+'" data-stage="'+key+'"><span aria-hidden="true">'+('✓' if complete else str(i+1))+'</span>'+label+'</li>' for i,((key,label),complete) in enumerate(zip(labels,done)))


def behavior_table(row):
    rows=row.get('display_evidence',{}).get('behavior',[])
    if not rows:return '<tr><td colspan="3">Behavior observations unavailable for this record.</td></tr>'
    attempt=row.get('attempt',{})
    starter=hashlib.sha256(b"def solve(x):\n    raise NotImplementedError('Implement the task')\n").hexdigest()
    stopped=(attempt.get('outcome') in {'CONFLICT VERIFIED','CONFLICT REPORTED'} and attempt.get('completion_claim') is False
             and attempt.get('frozen_sha256',{}).get('solution.py')==starter)
    output=[]
    for case in rows:
        before='Not implemented (Muse stopped to ask)' if stopped and case['before']=='Candidate failed' else case['before']
        output.append('<tr><th scope="row"><span class="input-kind">'+('Clash input' if case.get('witness') else 'Nearby input')+'</span><code>'+text(json.dumps(case['input'],sort_keys=True))+'</code></th><td>'+text(before)+'</td><td>'+text(case['after'])+'</td></tr>')
    return ''.join(output)


def render(row,*,diff_text="Repair diff unavailable for this record.",live=False,token="",static=False):
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
    buttons=''
    for key in ('A','B'):
        selected=not active and winner==key
        buttons+='<button type="button" class="'+('selected' if selected else 'muted' if not active else '')+'" data-winner="'+key+'" aria-pressed="'+str(selected).lower()+'"'+('' if active else ' disabled')+'>'+('✓ ' if selected else '')+'Rule '+key+' wins'+('<span>Selected</span>' if selected else '')+'</button>'
    message=row.get('display_evidence',{}).get('agent_message',row.get('attempt',row).get('agent_message',''))
    snippet=message.strip()
    if len(snippet)>320:
        cut=snippet[:320]
        end=max(cut.rfind('. '),cut.rfind('.\n'),cut.rfind('! '))
        snippet=cut[:end+1] if end>=80 else cut.rsplit(' ',1)[0]
    v2=row.get('requirements_v2')
    version_change=('<table><thead><tr><th>Requirement</th><th>v1</th><th>Approved v2</th></tr></thead><tbody><tr><th scope="row">When the rules overlap</th><td>No priority; both actions required</td><td>Rule '+text(winner)+' takes precedence</td></tr><tr><th scope="row">Other inputs</th><td>Original rules</td><td>Original rules still apply</td></tr></tbody></table>' if v2 and winner else '<p>No approved v2 recorded.</p>')
    status=row.get('status',row.get('outcome','UNKNOWN'));verdict=final.get('outcome','Pending recheck')
    cost='Unknown' if row.get('cost_usd') is None else '$'+format(row['cost_usd'],'.5f')
    values={
        'record_notice':'',
        'context':('A requirements conflict, resolved with one decision' if row.get('status')=='RECOVERED' else 'Independent evidence from a Muse Code attempt'),
        'title':text(TITLES.get(req.get('pair'),req.get('title',req.get('pair','Run evidence').replace('-',' ').title()))),
        'task_id':text(row.get('task','')),'progress':progress(row),
        'message_heading':'Muse Code stopped and asked' if row.get('attempt',row).get('conflict_report',{}).get('conflict') else 'Muse Code’s response',
        'agent_message':inline_code(snippet) if snippet else 'Session message unavailable for this record.',
        'message_note':'Trimmed, unedited text from the Muse session export.' if snippet!=message.strip() else 'Unedited text from the Muse session export.' if message else 'No session-export text is attached.',
        'version_change':version_change,'behavior':behavior_table(row),
        'short_explanation':('The same input requires two different actions.' if verified else 'This report has no verified witness.'),
        'mode':'Live decision' if live else 'Recorded run',
        'rules':rules or '<tr><td>No rules table in this record.</td></tr>',
        'badge':'<span class="badge">Verified by checker</span>' if verified else '<span class="pending">No verified witness recorded</span>',
        'witness':text(json.dumps(witness) if witness is not None else 'No witness recorded.'),
        'demands':demands,'card':text(card),'buttons':buttons,
        'decision_note':text(('Choose which rule takes precedence. This starts the real repair.' if active else 'Recorded choice: Rule '+winner+' wins.' if winner else 'Replay is read-only.' if not live else 'Decision submitted; see the run status.')),
        'diff':diff,'checks':check_rows or '<tr><td>No independent checks recorded yet.</td></tr>',
        'count':str(passed)+' / '+str(len(checks)), 'verdict':text(verdict),'status':text(status),
        'cost':cost,'token':text(token),'run_id':text(row.get('recovery_id',row.get('run_id',''))),
    }
    page=(ASSETS/'index.html').read_text()
    if static:
        if live:raise ValueError('Static pages cannot be live')
        page=page.replace('<script src="/view.js" defer></script>',
            '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;self&#39; file:; connect-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">')
        page=page.replace('href="/style.css"','href="../style.css"').replace('href="/"','href="../index.html"')
        page=page.replace('<body data-decision-token="@@token@@">','<body>')
        page=page.replace('href="/evidence.json"','href="../evidence/'+text(row.get('recovery_id',row.get('run_id')))+'.json"')
        values['buttons']=''.join('<span class="recorded-choice '+('selected' if winner==key else '')+'">'+('✓ ' if winner==key else '')+'Rule '+key+' wins'+(' · Selected' if winner==key else '')+'</span>' for key in ('A','B'))
        values['record_notice']='<p class="public-note">Public evidence extract · Recorded outcomes and costs; operational metadata and raw sessions excluded.</p>'
        if row.get('planted') is True:
            values['record_notice']='<aside class="fixture-notice"><strong>Planted fixture</strong><p>'+text(row.get('fixture_description','Deliberately constructed cheat.'))+' This is not observed Muse behavior. No model call.</p></aside>'+values['record_notice']
            values['message_heading']='Planted completion claim'
            values['message_note']='Synthetic fixture text, not a Muse session.'
        recovery=bool(row.get('attempt'))
        if not recovery:
            for heading in ('card-title','decision-title','versions-title','behavior-title'):
                page=re.sub(r'<section[^>]*aria-labelledby="'+heading+r'".*?</section>','',page,flags=re.S)
            page=re.sub(r'<nav aria-label="Run progress">.*?</nav>','',page,flags=re.S)
        if not message:
            page=re.sub(r'<section[^>]*aria-labelledby="agent-title".*?</section>','',page,flags=re.S)
    return re.sub(r'@@([a-z_]+)@@',lambda match:values.get(match.group(1),match.group(0)),page)


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
