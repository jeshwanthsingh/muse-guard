"""One recorded page: source, confirmed rules, decision, v2, implementation, checks."""
import base64,json,copy
from html import escape
from spec_guard.view import render as render_spec
from spec_guard.core import space,domain_errors

def e(value):return escape(str(value),quote=True)
def render(row):
 spec=row['spec'];display=copy.deepcopy(spec);unique={}
 for item in display['validation']['unconverted']:
  quote=item['quote']
  if quote not in unique:unique[quote]=item
  elif item['reason'] not in unique[quote]['reason']:unique[quote]['reason']+='; '+item['reason']
 display['validation']['unconverted']=list(unique.values());page=render_spec(display)
 page=page.replace('Find the clash before writing code.','From requirements to an independently checked implementation.')
 page=page.replace('<span>No coding agent invoked</span>','<span>'+('Fake model responses only' if row['response_kind']=='fake' else 'Recorded Muse Code implementation')+'</span>')
 page=page.replace('Spec review · Recorded run','Spec → decision → recheck · Recorded run')
 page=page.replace('<div class="stats">','<div class="stats"><span>Outcome: '+e(row.get('outcome',row['status']))+'</span>',1)
 declared=0 if domain_errors(spec['confirmed']['input_space']) else len(space(spec['confirmed']['input_space']))
 rejected=sum(d['decision']=='rejected' for d in spec['decisions'])
 invalid=sum(d['decision']=="couldn't convert" for d in spec['decisions'])
 boundary='<section class="panel"><h2>What was checked</h2><p><strong>'+str(row.get('checked_input_count',0))+' / '+str(declared)+' declared inputs checked against the approved rule table.</strong></p><p>'+str(rejected)+' rejected rules · '+str(invalid)+' invalid proposals · '+str(len(unique))+' sentences not converted (including context).</p><p>Conflict search finds every conflicting action among the confirmed rules and declared inputs.</p><p class="note"><strong>What this does NOT check:</strong> whether the English was translated correctly, omitted requirements, undeclared inputs, or real-world system behavior. One action is returned per input.</p></section>'
 page=page.replace('<section class="panel"><h2>Source requirements',boundary+'<section class="panel"><h2>Source requirements',1)
 extras='<section class="panel"><h2>Developer decision → approved rules</h2>'
 if row.get('decision'):
  extras+='<p>Selected priority: <strong>'+e(' → '.join(row['decision']['priority_order']))+'</strong></p><p>The first matching rule chooses the one next action. Version 1 is preserved; approved version 2 synchronizes the agent requirements and visible tests.</p>'
 else:extras+='<p>'+('No conflict required a priority decision.' if row['status']!='AWAITING DECISION' else 'Waiting for the developer’s CLI decision.')+'</p>'
 extras+='</section>'
 implementation=row.get('implementation')
 if implementation:
  checks=implementation['checks'];extras+='<section class="panel"><h2>Implementation → independent recheck</h2><p><strong>'+e(row.get('outcome',row['status']))+'</strong> · '+e(row.get('checked_input_count',0))+' approved inputs checked.</p><p>Original tests edited: '+('yes' if checks['original_tests_edited'] else 'no')+' — descriptive only; behavior decides the result.</p><details><summary>Show code changes</summary><pre><code>'+e(implementation['diff'])+'</code></pre></details><table><thead><tr><th>Check</th><th>Input → expected action</th><th>Layer</th><th>Result</th></tr></thead><tbody>'
  for test,case in zip(checks['tests'],row.get('check_inputs',[])):
   extras+='<tr><td>'+e(test['id'])+'</td><td><code>'+e(json.dumps(case[0]))+' → '+e(case[1])+'</code></td><td>'+e(test['layer'])+'</td><td>'+e(test['status'])+'</td></tr>'
  extras+='</tbody></table></section>'
 if row.get('error'):extras+='<section class="panel"><h2>Stopped</h2><p>'+e(row['error'])+'</p></section>'
 payload=json.dumps(row,indent=2)+'\n';href='data:application/json;base64,'+base64.b64encode(payload.encode()).decode()
 footer='<footer><p class="hash">One continuous record · '+e(row['status'])+' · '+('Fake responses; not model-quality evidence' if row['response_kind']=='fake' else 'Recorded provider calls')+'</p><a class="download" href="'+href+'" download="continuous-run.json">Download evidence record</a></footer></main></body></html>'
 page=page.split('<footer>')[0]+extras+footer
 return page
