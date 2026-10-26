"""Static local spec review page; no model execution, scripts or live controls."""
import base64
from html import escape
import json
from pathlib import Path
from .core import sentences


def show(value):return escape(str(value),quote=True)


def render(record):
    decisions={d['key']:d['decision'] for d in record['decisions']}
    quotes={}
    for item in record['validation']['items']:
        if isinstance(item['proposal'],dict) and item['proposal'].get('quote') in sentences(record['doc']):
            quotes.setdefault(item['proposal']['quote'],[]).append(decisions[item['key']])
    chunks=[];offset=0
    # Match whole recorded source sentences in their original document order.
    for sentence in sentences(record['doc']):
        start=record['doc'].find(sentence,offset)
        chunks.append(show(record['doc'][offset:start]))
        state='confirmed' if 'confirmed' in quotes.get(sentence,[]) else 'rejected' if sentence in quotes else 'context'
        chunks.append('<mark class="'+state+'">'+show(sentence)+'</mark>');offset=start+len(sentence)
    chunks.append(show(record['doc'][offset:]))
    rows=[]
    for item in record['validation']['items']:
        proposal=item['proposal'] if isinstance(item['proposal'],dict) else {}
        condition=json.dumps(proposal.get('when'),ensure_ascii=False) if item['kind']=='rule' else 'otherwise (fallback)'
        status=decisions[item['key']]
        rows.append('<tr><td class="quote">'+show(proposal.get('quote','Malformed proposal'))+'</td><td><strong>'+show(proposal.get('id','DEFAULT'))+'</strong><code>'+show(condition)+' → '+show(proposal.get('action','?'))+'</code></td><td><span class="state '+('confirmed' if status=='confirmed' else 'rejected')+'">'+show(status)+'</span>'+''.join('<small>'+show(error)+'</small>' for error in item['errors'])+'</td></tr>')
    cards=[]
    for i,clash in enumerate(record['clashes'],1):
        cards.append('<article class="clash"><div class="card-head"><h3>Clash '+str(i)+'</h3><span class="verified">✓ Verified by exhaustive search</span></div><code class="witness">'+show(json.dumps(clash['witness'],ensure_ascii=False))+'</code><div class="demands">'+''.join('<p><strong>Rule '+show(rule)+'</strong> requires <code>'+show(action)+'</code></p>' for rule,action in zip(clash['rules'],clash['actions']))+'</div><p class="note">Verified against the confirmed table. The developer still owns whether that table expresses the intended English.</p></article>')
    unresolved=''.join('<li><q>'+show(item['quote'])+'</q><p>'+show(item['reason'])+'</p></li>' for item in record['validation']['unconverted'])
    payload=json.dumps(record,indent=2,allow_nan=False).encode()
    href='data:application/json;base64,'+base64.b64encode(payload).decode()
    confirmed=sum(d['decision']=='confirmed' for d in record['decisions'])
    mode='Fake Spark response · offline fixture' if record['response_kind']=='fake' else 'Recorded Spark extraction'
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>Spec review — muse-guard</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f9fc;color:#172438;font:17px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{background:white;border-bottom:1px solid #dbe2ee;padding:18px max(32px,calc((100vw - 1120px)/2));display:flex;align-items:center;gap:24px}header strong{font-size:23px}header span{background:#e9edf4;border-radius:5px;padding:4px 12px;font-size:14px}main{max-width:1120px;margin:auto;padding:28px 0 48px}h1{font-size:36px;margin:0 0 8px;line-height:1.2}h2{font-size:23px;margin:0 0 14px}h3{font-size:21px;margin:0}.lead{margin:0 0 22px;color:#52647d}.stats{display:flex;gap:14px;margin-bottom:22px}.stats span{padding:8px 14px;border:1px solid #dbe2ee;background:white;border-radius:6px;font-size:15px}.panel{padding:22px 24px;border:1px solid #dbe2ee;border-radius:8px;background:white;margin-bottom:20px}.document{white-space:pre-wrap;font-size:16px;margin:0;line-height:1.8}.document mark{padding:2px 0;background:transparent;color:inherit}.document mark.confirmed{background:#e0f1e6}.document mark.rejected{background:#fce6de}.legend,.note,small{font-size:13px;color:#52647d}.legend{margin:12px 0 0}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left}th{font-size:13px;color:#52647d;border-bottom:1px solid #dbe2ee;padding:8px}td{padding:12px 8px;border-bottom:1px solid #e7ebf1;vertical-align:top;font-size:15px}.quote{width:42%}td code,small{display:block}code{font:14px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}td strong{font-size:13px}.state{font-size:12px;padding:3px 8px;border-radius:4px;white-space:nowrap}.state.confirmed{background:#e0f1e6;color:#146542}.state.rejected{background:#fce6de;color:#9e3030}.clash{border:1px solid #dbe2ee;border-left:4px solid #d5a42c;background:white;border-radius:8px;padding:22px 24px;margin-bottom:16px}.card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.verified{font-size:13px;color:#146542;background:#e0f1e6;padding:4px 10px;border-radius:20px}.witness{display:block;background:#f1f4f9;padding:12px 16px;border-radius:5px}.demands{display:flex;gap:32px}.demands p{margin:14px 0 4px}.note{margin-bottom:0}details summary{cursor:pointer;color:#2454bb}li{margin:12px 0}li p{font-size:14px;color:#52647d;margin:3px 0}.download{display:inline-block;background:#2454bb;color:white;border-radius:6px;padding:12px 20px;text-decoration:none;font-weight:650}footer{display:flex;justify-content:space-between;align-items:center;gap:24px;margin-top:26px}.hash{max-width:650px;overflow-wrap:anywhere;font-size:12px;color:#52647d}a:focus-visible,summary:focus-visible{outline:3px solid #9b6b00;outline-offset:4px}@media(max-width:1180px){main{margin:0 28px}}@media(max-width:700px){main{margin:0 16px}header{padding:16px;gap:12px}header span{font-size:12px}h1{font-size:28px}.stats,.card-head,footer,.demands{flex-wrap:wrap}.panel,.clash{padding:18px}.quote{min-width:230px}}
</style></head><body><header><strong>muse-guard</strong><span>Spec review · Recorded run</span></header><main><h1>Find the clash before writing code.</h1><p class="lead">'''+show(mode)+''' · Source-linked rules, reviewed by the developer.</p><div class="stats"><span>'''+str(confirmed)+''' confirmed items</span><span>'''+str(len(record['clashes']))+''' verified clashes</span><span>No coding agent invoked</span></div><section class="panel"><h2>Source requirements</h2><div class="document">'''+''.join(chunks)+'''</div><p class="legend">Green: confirmed source sentence · Red: rejected or unconverted proposal · Plain: context or not converted</p></section><section class="panel"><h2>Sentence → proposed rule → decision</h2><div class="table-wrap"><table><thead><tr><th>Exact source sentence</th><th>Condition → action</th><th>Developer review</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div></section><section><h2>Clashes found before coding</h2>'''+(''.join(cards) or '<div class="panel">No clashes in the confirmed finite table. This does not establish that the English was extracted correctly.</div>')+'''</section><section class="panel"><h2>Rejected / couldn’t convert / uncovered</h2><p>'''+str(sum(d['decision']!='confirmed' for d in record['decisions']))+''' rejected or invalid proposals; see their reasons in the table.</p><details><summary>Review sentences without a converted rule ('''+str(len(record['validation']['unconverted']))+''')</summary><ul>'''+unresolved+'''</ul></details><p class="note">Uncovered inputs without an approved fallback: '''+str(len(record['uncovered_inputs']))+'''. No default behavior is invented.</p>'''+''.join('<p>'+show(error)+'</p>' for error in record['validation']['errors'])+'''</section><footer><p class="hash">Document SHA-256: '''+show(record['doc_sha256'])+'''<br>Model: '''+show(record['model'])+'''</p><a class="download" href="'''+href+'''" download="spec-record.json">Download spec evidence</a></footer></main></body></html>'''


def save(record,out):
    out=Path(out)
    if out.exists():raise ValueError('Choose a new output directory; existing evidence is never overwritten')
    out.mkdir(parents=True)
    (out/'record.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    # JSON is a strict YAML subset, as in the existing task catalog.
    (out/'confirmed.yaml').write_text(json.dumps(record['confirmed'],indent=2,allow_nan=False)+'\n')
    (out/'index.html').write_text(render(record))
    return out
