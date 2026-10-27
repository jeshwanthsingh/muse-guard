"""Separate preregistered external-authored scorer. Original scorer unchanged."""
import argparse,copy,hashlib,json,re,subprocess
from collections import Counter
from pathlib import Path
from spec_guard.core import review,space,matches
from spec_guard.provider import propose,today
ROOT=Path(__file__).resolve().parents[1]
SET=ROOT/'spec_eval/human'
def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def words(text):return ' '.join(text.split())
def document(text):return '\n\n'.join(words(p) for p in text.split('\n\n'))
def normalize(proposal,truth):
 p=copy.deepcopy(proposal)
 if not isinstance(p,dict):return p
 aliases={alias:key for key,values in truth['field_aliases'].items() for alias in values}
 def fields(value):
  if not isinstance(value,dict):return value
  renamed={aliases.get(k,k):v for k,v in value.items()}
  if len(renamed)!=len(value):raise ValueError('Colliding field aliases')
  return renamed
 if 'input_space' in p:p['input_space']=fields(p['input_space'])
 for r in p.get('rules',[]) if isinstance(p.get('rules'),list) else []:
  if isinstance(r,dict):
   if isinstance(r.get('quote'),str):r['quote']=words(r['quote'])
   if 'when' in r:r['when']=fields(r['when'])
 for r in [p.get('default')]+(p.get('unconverted',[]) if isinstance(p.get('unconverted'),list) else []):
  if isinstance(r,dict) and isinstance(r.get('quote'),str):r['quote']=words(r['quote'])
 return p
def score(doc,proposal,truth,*,response_kind="fake",cost=None):
 try:p=normalize(proposal,truth)
 except ValueError:p={'invalid':'Colliding field aliases'}
 r=review(document(doc),p,lambda item:True,response_kind=response_kind,cost=cost)
 inputs=space(truth['proposal']['input_space'])
 def action(a):return next((k for k,v in truth['action_aliases'].items() if a in v),a)
 def key(rule,kind):
  cases='fallback' if kind=='default' else tuple(canon(v) for v in inputs if matches(rule,v))
  return (words(rule['quote']),action(rule['action']),cases)
 wanted=Counter(key(x,'rule') for x in truth['proposal']['rules'])
 if 'default' in truth['proposal']:wanted[key(truth['proposal']['default'],'default')]+=1
 found=Counter();invalid=0
 for item in r['validation']['items']:
  if not item['valid']:invalid+=1;continue
  try:found[key(item['proposal'],item['kind'])]+=1
  except (KeyError,TypeError,ValueError):invalid+=1
 def clash(witness,quotes,actions):return (canon(witness),tuple(sorted(zip(quotes,map(action,actions)))))
 byid={x['id']:x for x in truth['proposal']['rules']}
 wc={clash(c['witness'],[byid[i]['quote'] for i in c['rules']],c['actions']) for c in truth['clashes']}
 fc={clash(c['witness'],c['quotes'],c['actions']) for c in r['clashes']}
 def domain(v):return {k:sorted(canon(x) for x in values) for k,values in v.items()}
 try:equal=domain(r['confirmed']['input_space'])==domain(truth['proposal']['input_space'])
 except (TypeError,ValueError,AttributeError):equal=False
 m={'rules_correct':sum((wanted&found).values()),'rules_truth':sum(wanted.values()),'rules_wrong':sum((found-wanted).values())+invalid,'rules_missing':sum((wanted-found).values()),'clashes_found':len(wc&fc),'clashes_truth':len(wc),'clashes_missed':len(wc-fc),'clashes_false':len(fc-wc),'domains_correct':equal,'schema_errors':len(r['validation']['errors']),'invalid_unconverted':sum(x.get('source_verified') is False for x in r['validation']['unconverted'])}
 m['success']=equal and not any(m[k] for k in ('rules_wrong','rules_missing','clashes_missed','clashes_false','schema_errors','invalid_unconverted'))
 return m,r

def verify():
 manifest=SET/'MANIFEST.json';m=json.loads(manifest.read_text())
 if subprocess.check_output(['git','show','HEAD:spec_eval/human/MANIFEST.json'],cwd=ROOT)!=manifest.read_bytes():raise ValueError('Manifest must be committed before real calls')
 for name,h in m['files'].items():
  p=ROOT/name
  if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('External set freeze drift: '+name)
 return m

def evaluate(out):
 if today()!='2026-10-27':raise ValueError('Preregistered date is Oct27')
 m=verify();out=Path(out)
 if out.exists():raise ValueError('Never repeat or overwrite this evaluation')
 out.mkdir(parents=True)
 report={'set':'Claude-authored, user-reviewed; separate from original eight','status':'STARTED','entries':[],'manifest_sha256':hashlib.sha256((SET/'MANIFEST.json').read_bytes()).hexdigest()}
 def save():(out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
 save()
 for name in m['order']:
  verify();doc=(SET/(name+'.md')).read_text()
  try:
   # Source text only; no truth or alias tables are sent to the model.
   proposal,cost=propose(doc)
   truth=json.loads((SET/'truth'/(name+'.json')).read_text());measures,reviewed=score(doc,proposal,truth,response_kind="real",cost=cost)
   entry={'document':name,'source_sha256':hashlib.sha256(doc.encode()).hexdigest(),'proposal':proposal,'measures':measures,'cost':cost,'normalized_review':reviewed}
   report['entries'].append(entry);save()
  except (ValueError,OSError,KeyError,TypeError) as error:
   report.update(status='STOPPED',error=str(error),stopped_document=name);save();return report
 report.update(status='COMPLETE',cost_usd=sum(e['cost']['cost_usd'] for e in report['entries']));save();return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--real',action='store_true',required=True);a=p.parse_args()
 print(json.dumps(evaluate(a.out),indent=2))
