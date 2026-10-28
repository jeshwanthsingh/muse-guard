"""Display-only decision consequences, using the unchanged exhaustive checker."""
import copy
import itertools
import json
from html import escape
from muse_guard.quality_gate import input_space
from muse_guard.rules import actions, verify_conflict


def preview(requirements):
    req=copy.deepcopy(requirements)
    req['rules']=[r for r in req['rules'] if r.get('enabled',True)]
    if req.get('priority'):
        raise ValueError('Preview requires original unprioritized requirements')
    values=input_space(req)
    groups=[]
    for a,b in itertools.combinations(req['rules'],2):
        witnesses=[v for v in values if verify_conflict(req,{'conflict':True,'rules':[a['id'],b['id']],
                   'witness':v,'explanation':'Decision preview exhaustive search'})['verified']]
        if not witnesses:continue
        ids=[a['id'],b['id']]
        rest=[r['id'] for r in req['rules'] if r['id'] not in ids]
        choices=[{'winner':ids[0],'priority':ids+rest},{'winner':ids[1],'priority':ids[::-1]+rest}]
        variants=[dict(req,priority=c['priority']) for c in choices]
        rows=[]
        for value in values:
            outcomes=[actions(v,value)[0] for v in variants]
            if outcomes[0]!=outcomes[1]:rows.append({'input':value,'actions':outcomes})
        groups.append({'rules':ids,'affected_inputs':len(rows),'choices':choices,'rows':rows})
    return {'checked':len(values),'conflicts':len(groups),'groups':groups}


def summary(group):
    n=group['affected_inputs']
    return '1 conflict ('+' vs '.join(group['rules'])+'), '+str(n)+' input'+('' if n==1 else 's')+' affected'


def cli_preview(req):
    data=preview(req)
    lines=['Decision preview — '+str(data['checked'])+' declared inputs checked']
    for group in data['groups']:
        lines.append(summary(group))
        lines.append('Input -> '+' | '.join(c['winner']+' wins' for c in group['choices']))
        for row in group['rows']:
            lines.append(json.dumps(row['input'],sort_keys=True)+' -> '+' | '.join(row['actions']))
        lines.append('Other declared inputs have the same outcome under either choice.')
        if len(req['rules'])>2:
            lines.append('Compared total orders: '+' vs '.join(' > '.join(c['priority']) for c in group['choices']))
    if not data['groups']:lines.append('No conflicting actions in this declared table.')
    return '\n'.join(lines)


def html_preview(req):
    data=preview(req)
    e=lambda x:escape(str(x),quote=True)
    html='<section class="panel decision-preview" aria-label="Decision preview"><h2>Decision preview</h2><p>'+str(data['checked'])+' declared inputs checked. Only inputs whose outcomes differ between choices are listed.</p>'
    for group in data['groups']:
        html+='<article class="preview-group"><h3>'+e(summary(group))+'</h3><div class="table-wrap"><table><thead><tr><th scope="col">Declared input</th>'
        html+=''.join('<th scope="col">'+e(c['winner'])+' wins</th>' for c in group['choices'])+'</tr></thead><tbody>'
        for row in group['rows']:
            html+='<tr><th scope="row"><code>'+e(json.dumps(row['input'],sort_keys=True))+'</code></th>'+''.join('<td><code>'+e(a)+'</code></td>' for a in row['actions'])+'</tr>'
        html+='</tbody></table></div><p>Other declared inputs have the same outcome under either choice.</p>'
        if len(req['rules'])>2:html+='<p>Compared total orders: '+e(' vs '.join(' > '.join(c['priority']) for c in group['choices']))+'</p>'
        html+='</article>'
    if not data['groups']:html+='<p>No conflicting actions among these rules and declared inputs.</p>'
    return html+'<p class="note">Preview of rule-table consequences, not a code execution result. It does not validate extraction or undeclared inputs.</p></section>'
