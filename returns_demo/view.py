# Read-only evidence for actual HTTP traffic and a recorded service edit.
import base64
from html import escape
import json
from submission_tools.decision_preview import html_preview


def e(value):return escape(str(value),quote=True)
def pretty(value):return e(json.dumps(value,indent=2,ensure_ascii=False))


def witness_response(phase):
    return next((r['response'] for r in phase.get('http',[]) if r.get('check')=='policy.test_case_0' and r['request']['method']=='POST' and r['request']['path'].endswith('/evaluate')),None)


def response_card(label,response):
    return '<article class="http"><h3>'+e(label)+'</h3>'+('<p>HTTP '+e(response['status'])+' · application/json</p><pre>'+pretty(response['json'])+'</pre>' if response else '<p>Not run yet.</p>')+'</article>'


def render(row):
    fake=row['response_kind']=='fake';baseline=row.get('baseline',{});final=row.get('final',{})
    policy=[r for r in final.get('tests',[]) if r['id'].startswith('policy.')]
    regressions=[r for r in final.get('tests',[]) if r['id'].startswith('regression.')]
    cost='unknown' if row.get('cost_usd') is None else '$'+format(row['cost_usd'],'.5f')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>Returns service — muse-guard</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f8fb;color:#172438;font:17px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{background:white;border-bottom:1px solid #dbe2ee;padding:18px max(32px,calc((100vw - 1120px)/2));display:flex;gap:24px;align-items:center}header strong{font-size:24px}header span{font-size:14px;background:#e9edf4;padding:4px 12px;border-radius:5px}main{max-width:1120px;margin:24px auto 48px}h1{font-size:34px;line-height:1.15;margin:0 0 10px}h2{font-size:24px;margin:0 0 12px}h3{font-size:18px;margin:0 0 10px}p{margin:8px 0}.lead,.note{color:#52647d}.note{font-size:14px}.notice{padding:14px 18px;background:#fff3d6;border:1px solid #e1b76d;border-radius:7px;margin:16px 0}.stats{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.stats span,.badge{background:#e0f1e6;color:#146542;padding:6px 12px;border-radius:5px;font-size:15px}.panel{background:white;border:1px solid #dbe2ee;border-radius:8px;padding:22px 24px;margin:20px 0}.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}.http{border:1px solid #dbe2ee;border-radius:6px;padding:16px;background:#f8fafd}.http p{font-size:14px;color:#52647d}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;margin:10px 0 0}code{font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}.rules,table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid #dbe2ee;font-size:15px}th{font-weight:650}.table-wrap{overflow:auto}.preview-group{background:#fff7e9;border:1px solid #e1b76d;border-radius:6px;padding:16px;margin-top:12px}.preview-group p{font-size:14px}.preview-group th:first-child{width:60%}.selected{font-size:22px;font-weight:700;color:#146542}.check-pass{color:#146542;font-weight:700}.check-fail{color:#a52727;font-weight:700}.download{display:inline-block;background:#2454bb;color:white;text-decoration:none;padding:12px 18px;border-radius:6px}nav{display:flex;gap:16px;flex-wrap:wrap;font-size:15px}a{color:#2454bb}a:focus-visible,summary:focus-visible{outline:3px solid #2454bb;outline-offset:4px}.scope{border-left:4px solid #2454bb}details summary{cursor:pointer;color:#2454bb}@media(max-width:1180px){main{margin:24px 24px 48px}}@media(max-width:700px){.cols{grid-template-columns:1fr}header{padding:16px;gap:10px}h1{font-size:28px}.panel{padding:16px}main{margin:18px 14px}}
</style></head><body><header><strong>muse-guard</strong><span>Returns service · Recorded run</span></header><main>'''
    page+='<h1>A real service, one policy decision.</h1><p class="lead">Baseline HTTP → reviewed rules → developer choice → service code edit → independent HTTP checks.</p>'
    page+='<div class="notice"><strong>'+('Fake model responses · offline end-to-end fixture' if fake else 'Recorded Muse Spark + Muse Code run')+'</strong><p>'+('The model replies and choice are constructed. The service requests, sandbox denials and independent HTTP checks below actually ran. This is not model-quality evidence.' if fake else 'Next actions are simulated; no money moves. Each real translation and the decision require explicit human input.')+'</p></div>'
    page+='<div class="stats"><span>'+e(row.get('outcome',row['status']))+'</span><span>'+str(sum(r['status']=='PASS' for r in policy))+'/4 policy cases</span><span>'+str(sum(r['status']=='PASS' for r in regressions))+'/7 existing regressions</span><span>Model cost '+cost+'</span></div>'
    page+='<nav aria-label="Evidence sections"><a href="#baseline">Baseline</a><a href="#clash">Clash and preview</a><a href="#decision">Decision</a><a href="#responses">Before / after HTTP</a><a href="#checks">All checks</a></nav>'
    before=witness_response(baseline);after=witness_response(final)
    page+='<section class="panel" id="baseline"><h2>1. Baseline service: actual HTTP response</h2><p>Eligible + fraud hold, amount 2500 cents. Original policy ignores fraud hold.</p>'+response_card('POST /returns/r1/evaluate',before)+'<p class="note">Event-built baseline commit '+e(row['baseline_commit'])+'. Source hashes and all actual requests/responses are in the evidence record.</p></section>'
    page+='<section class="panel" id="clash"><h2>2. The policy requirements clash</h2>'
    req=row.get('requirements_v1')
    if req:
        page+='<table><thead><tr><th>Rule</th><th>Reviewed source sentence</th><th>Next action</th></tr></thead><tbody>'
        for rule in req['rules']:page+='<tr><th>'+e(rule['id'])+'</th><td>'+e(rule['text'])+'</td><td><code>'+e(rule['action'])+'</code></td></tr>'
        group=row.get('decision_preview',{}).get('groups',[{}])[0]
        witness=group.get('rows',[{}])[0].get('input',{})
        page+='</tbody></table><p><span class="badge">Verified by exhaustive checker</span> These rules require different actions for <code>'+e(json.dumps(witness))+'</code>.</p>'
    else:page+='<p>Waiting for reviewed rule translations.</p>'
    spec=row.get('spec')
    if spec:
        page+='<details><summary>Show source → proposed rule → review decisions</summary><table><thead><tr><th>Exact sentence</th><th>Proposal</th><th>Review</th></tr></thead><tbody>'
        for item,d in zip(spec['validation']['items'],spec['decisions']):
            proposal=item['proposal'];page+='<tr><td>'+e(proposal.get('quote',''))+'</td><td><code>'+e(json.dumps(proposal.get('when','otherwise')))+' → '+e(proposal.get('action',''))+'</code></td><td>'+e(d['decision'])+'</td></tr>'
        page+='</tbody></table></details>'
    page+='</section>'
    if req:page+=html_preview(req)
    page+='<section class="panel" id="decision"><h2>3. Developer decision → approved v2</h2>'
    if row.get('decision'):
        page+='<p class="selected">✓ Rule '+e(row['decision']['winner'])+' wins</p><p>'+e(row['decision_provenance'])+'</p><p>Version 1 is preserved. Approved v2 synchronizes service instructions and visible policy tests; the seven existing HTTP regression tests stay unchanged.</p>'
    else:page+='<p>Waiting for the developer in the CLI. No service edit starts before the choice.</p>'
    page+='</section><section class="panel" id="diff"><h2>4. Service code change</h2>'
    agent=row.get('agent')
    if agent:
        page+='<p>'+e(agent['kind'])+'</p><blockquote>'+e(agent.get('claim','No completed session message retained.'))+'</blockquote><details open><summary>Actual source diff</summary><pre><code>'+e(agent.get('diff') or 'No completed source diff retained.')+'</code></pre></details>'
        page+='<p class="note">Agent edited original tests: '+('yes' if agent.get('original_tests_edited') is True else 'no' if agent.get('original_tests_edited') is False else 'unknown')+' (descriptive). Agent exit code never decides the independent result.</p>'
    else:page+='<p>Not run yet.</p>'
    page+='</section><section class="panel" id="responses"><h2>5. Same fraud-held request, before → after</h2><p><code>{"eligible": true, "fraud_hold": true, "amount_cents": 2500}</code></p><div class="cols">'+response_card('Before policy change',before)+response_card('After approved change',after)+'</div><p class="note">Actual HTTP observations. Each phase launches a fresh sandboxed in-memory service with the same synthetic request; this does not claim persistence across restarts.</p></section>'
    page+='<section class="panel" id="checks"><h2>6. Independent HTTP checks</h2><p>Original regression fixture restored outside the agent folder. All four approved policy inputs use real create → evaluate → get requests.</p><table><thead><tr><th>Check</th><th>Layer</th><th>Result</th></tr></thead><tbody>'
    for test in final.get('tests',[]):page+='<tr><th>'+e(test['id'])+'</th><td>'+e(test['layer'])+'</td><td class="'+('check-pass' if test['status']=='PASS' else 'check-fail')+'">'+e(test['status'])+'</td></tr>'
    page+='</tbody></table><p><strong>Final verdict: '+e(row.get('outcome','Pending independent recheck'))+'</strong></p></section><section class="panel scope"><h2>'+e(row['scope'])+'</h2><table><thead><tr><th>Declared input</th><th>Approved next action</th></tr></thead><tbody>'
    for case in final.get('cases',[]):page+='<tr><th><code>'+e(json.dumps(case['input']))+'</code></th><td>'+e(case['expected'])+'</td></tr>'
    page+='</tbody></table><p class="note">This does not exhaustively check concurrency, persistence, authentication, payments, omitted requirements, extraction accuracy or an arbitrary web service.</p></section>'
    if row.get('error'):page+='<section class="panel"><h2>Stopped</h2><p>'+e(row['error'])+'</p></section>'
    href='data:application/json;base64,'+base64.b64encode((json.dumps(row,indent=2)+'\n').encode()).decode()
    page+='<footer><a class="download" href="'+href+'" download="returns-service-run.json">Download evidence record</a><p class="note">'+e(row['run_id'])+' · '+e(row['status'])+' · Raw session data is stored separately, not embedded here.</p></footer></main></body></html>'
    return page
