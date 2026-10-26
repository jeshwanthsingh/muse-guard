"""Offline, allowlisted public evidence export. Never executes candidates or models."""
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from .view import ASSETS, TITLES, display_requirements, load_record, render, text

PUBLIC_PHASE = ('run_id','date','task','mode','stage','pricing_mode','model','outcome','cost_usd',
                'time_seconds','main_steps','model_invoked','completion_claim','claim_contradicted',
                'unauthorized_test_change','original_tests_edited','requirements_version','requirements_hash',
                'visible_tests_hash','hidden_tests_hash','agent_message','termination')


def select(row,keys):
    return {key:row[key] for key in keys if key in row}


def requirements(row):
    result=select(row,('id','pair','title','version','default','priority'))
    result['rules']=[select(rule,('id','text','when','action')) for rule in row.get('rules',[])]
    return result


def phase(row):
    result=select(row,PUBLIC_PHASE)
    result['tests']=[select(test,('id','status','layer')) for test in row.get('tests',[])]
    if 'tokens' in row:result['tokens']=select(row['tokens'] or {},('input','output','cached_input'))
    if 'conflict_report' in row:result['conflict_report']=select(row['conflict_report'],('conflict','rules','witness','explanation'))
    if 'conflict_validation' in row:result['conflict_validation']=select(row['conflict_validation'],('verified','rules','witness','actions'))
    if 'frozen_sha256' in row:result['frozen_sha256']=select(row['frozen_sha256'],('solution.py',))
    return result


def public_record(row,source_sha):
    """Explicit public fields only. Unknown fields never enter the site or downloads."""
    result=phase(row)
    result.update(select(row,('recovery_id','status','planted','fixture_description','repair_diff')))
    result['requirements_v1']=requirements(display_requirements(row))
    for key in ('attempt','repair'):
        if key in row:result[key]=phase(row[key])
    if 'requirements_v2' in row:result['requirements_v2']=requirements(row['requirements_v2'])
    if 'decision' in row:result['decision']=select(row['decision'],('winner','scope','rules','witness','source','simulated'))
    if 'conflict_card' in row:result['conflict_card']=select(row['conflict_card'],('text','cost_usd','time_seconds'))
    if 'display_evidence' in row:
        display=row['display_evidence']
        result['display_evidence']=select(display,('agent_message','agent_message_sha256','before_solution_sha256','after_solution_sha256'))
        result['display_evidence']['behavior']=[select(case,('input','witness','before','after')) for case in display.get('behavior',[])]
    result['publication']={'kind':'public evidence extract','source_sha256':source_sha,
        'note':'Selected recorded evidence; raw sessions, environment, request logs and local paths are excluded. Verdicts are not recomputed.'}
    encoded=json.dumps(result,allow_nan=False)
    if len(encoded)>1024*1024:raise ValueError('Public record exceeds size limit')
    scan_text(encoded)
    return result


PRIVATE_PATTERNS=(
    r'(?i)/(?:users|home|private/var|private/tmp)/', r'(?i)[a-z]:[\\/]+users[\\/]',
    r'(?i)\b(?:https?|wss?)://',
    r'(?i)\b[a-z0-9][a-z0-9.-]*\.(?:ts\.net|local|internal|lan|com|net|org|io|dev|ai|example)\b',
    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    r'(?i)\b(?:api[_-]?key|meta_api_key|model_api_key|password|secret|authorization|access_token)\s*["\x27]?\s*[:=]\s*["\x27]?[a-z0-9_+/.-]{8,}',
    r'\b(?:sk-|ghp_|github_pat_|AKIA)[A-Za-z0-9_-]{12,}',
    r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
    r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
)


def scan_text(value):
    for pattern in PRIVATE_PATTERNS:
        if re.search(pattern,value):raise ValueError('Public export refused: private path, hostname or credential pattern detected')


def describe(row):
    if row.get('planted'):return 'Planted fixture: an edited test cannot turn a failing implementation into a pass.'
    if row.get('status')=='RECOVERED':return 'Conflict reported → Rule '+row.get('decision',{}).get('winner','?')+' chosen → repair independently passed.'
    if row.get('outcome')=='PASS':return 'Solvable requirements implemented; independent visible and hidden checks passed.'
    return 'Recorded '+str(row.get('status',row.get('outcome','UNKNOWN'))).lower()+'; inspect the independent evidence.'


def title(row):
    req=row.get('requirements_v1',{})
    base=TITLES.get(req.get('pair'),req.get('title',row.get('task','Run evidence')))
    return base+(' · planted cheat' if row.get('planted') else '')


STATIC_CSS='''
.public-note{font-size:14px;color:#52647d;margin:0 0 22px}.fixture-notice{background:#fff0bf;border:1px solid #d5a42c;border-radius:8px;padding:18px 24px;margin-bottom:18px}.fixture-notice p{margin:6px 0 0;font-size:16px}.recorded-choice{padding:12px 22px;border:1px solid #b8c5d9;border-radius:6px;background:#eef2f8;color:#53647c;font-size:17px}.recorded-choice.selected{background:#2454bb;color:white;border-color:#2454bb}.site-intro{max-width:850px;margin:0 0 24px}.site-intro p{color:#52647d;font-size:18px;margin:14px 0}.run-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.run-card{display:block;background:white;padding:22px 24px;border:1px solid #dbe2ee;border-radius:8px;text-decoration:none;color:#172438;min-height:185px}.run-card:hover{border-color:#2454bb}.run-card h2{font-size:23px;margin:12px 0 8px}.run-card p{font-size:16px;margin:0 0 12px;color:#52647d}.card-meta{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:#52647d}.card-outcome{font-weight:700;color:#146542}.card-outcome.fixture{color:#805511}.card-link{color:#2454bb;font-size:15px;font-weight:650}.site-footer{font-size:14px;color:#52647d;margin-top:24px}.run-status span,.card-meta{font-variant-numeric:tabular-nums}@media(max-width:720px){.run-grid{grid-template-columns:1fr}.choices{flex-wrap:wrap}.recorded-choice{font-size:15px;padding:10px 14px}}
'''


def export_site(paths,out):
    out=Path(out).expanduser()
    if out.exists() or out.is_symlink():raise ValueError('Output already exists; choose a new folder')
    records=[];identities=set()
    for path in paths:
        path=Path(path);row=load_record(path)
        identity=row.get('recovery_id',row.get('run_id'))
        if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',identity):raise ValueError('Unsafe run identity')
        if identity in identities:raise ValueError('Duplicate run identity')
        identities.add(identity)
        record=public_record(row,hashlib.sha256(path.read_bytes()).hexdigest())
        records.append((identity,record))
    if not records:raise ValueError('Select at least one recorded run')
    files={'style.css':(ASSETS/'style.css').read_text()+STATIC_CSS,'.nojekyll':''}
    cards=[]
    for identity,row in records:
        payload=json.dumps(row,indent=2,allow_nan=False)+'\n'
        page=render(row,diff_text=row.get('repair_diff','Code diff not attached to this public record.'),static=True)
        # file:// navigation ignores download for another local file in Chrome.
        # A data URL downloads offline too; its bytes match the inspectable JSON.
        download='data:application/json;base64,'+base64.b64encode(payload.encode()).decode()
        page=page.replace('class="download" href="../evidence/'+identity+'.json"','class="download" href="'+download+'"')
        page=page.replace('Public evidence extract ·','<a href="../evidence/'+identity+'.json">Public evidence extract</a> ·')
        files['runs/'+identity+'.html']=page
        files['evidence/'+identity+'.json']=payload
        cost='Unknown' if row.get('cost_usd') is None else '$'+format(row['cost_usd'],'.5f')
        outcome=row.get('status',row.get('outcome','UNKNOWN'))
        cards.append('<a class="run-card" href="runs/'+identity+'.html"><div class="card-meta"><span class="card-outcome'+(' fixture' if row.get('planted') else '')+'">'+text(outcome)+'</span><span>'+text(cost)+'</span></div><h2>'+text(title(row))+'</h2><p>'+text(describe(row))+'</p><span class="card-link">'+('Planted fixture · ' if row.get('planted') else 'Recorded run · ')+'View evidence →</span></a>')
    files['index.html']='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' file:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>Recorded runs — muse-guard</title><link rel="stylesheet" href="style.css"></head><body><header><a class="brand" href="index.html">muse-guard <span class="brand-mark" aria-hidden="true">m / g</span></a><span class="record-label">Recorded run collection</span></header><main><div class="site-intro"><h1>When requirements clash,<br>stop, decide, repair.</h1><p>Explore recorded conflicts and independent checks. Each example includes its evidence record. Historical development examples, not a completed study.</p></div><div class="run-grid">'''+''.join(cards)+'''</div><p class="site-footer">Read-only demo · Opens offline · No live model calls<br>Planted cheats are labeled and excluded from claims about Muse behavior.</p></main></body></html>'''
    for content in files.values():scan_text(content)
    manifest={name:hashlib.sha256(content.encode()).hexdigest() for name,content in sorted(files.items())}
    files['manifest.json']=json.dumps({'schema':1,'kind':'static recorded demo','files':manifest,'privacy_scan':'passed built-in credential/path/hostname patterns'},indent=2)+'\n'
    out.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.muse-site-',dir=out.parent))
    try:
        for name,content in files.items():
            target=staging/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
        if out.exists():raise ValueError('Output appeared during export; refusing replacement')
        staging.rename(out)
    finally:
        if staging.exists():shutil.rmtree(staging)
    return out
