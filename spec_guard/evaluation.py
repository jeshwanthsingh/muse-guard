"""Preregistered extraction scoring; hand-written truth never enters model input."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from .core import review,matches,space
from .provider import propose,today
from .view import save

ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/'spec_eval'


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def score(doc,proposal,truth):
    record=review(doc,proposal,lambda item:True)
    aliases=truth.get('action_aliases',{})
    def action(value):return next((key for key,values in aliases.items() if value in values),value)
    inputs=space(truth['proposal']['input_space'])
    def rule_key(rule,kind='rule'):
        return (rule['quote'],action(rule['action']),tuple(canonical(value) for value in inputs if matches(rule,value)) if kind=='rule' else 'default')
    expected=Counter(rule_key(r) for r in truth['proposal']['rules'])
    expected[rule_key(truth['proposal']['default'],'default')]+=1
    observed=Counter();invalid=0
    for item in record['validation']['items']:
        if item['valid']:
            try:observed[rule_key(item['proposal'],item['kind'])]+=1
            except (KeyError,TypeError):invalid+=1
        else:invalid+=1
    correct=sum((expected&observed).values());wrong=sum((observed-expected).values())+invalid;missing=sum((expected-observed).values())
    def domains(d):return {key:sorted(canonical(v) for v in values) for key,values in d.items()}
    try:domain_match=domains(record['confirmed']['input_space'])==domains(truth['proposal']['input_space'])
    except (TypeError,ValueError):domain_match=False
    expected_by_id={r['id']:r for r in truth['proposal']['rules']}
    def clash_key(witness,pairs):return (canonical(witness),tuple(sorted((quote,action(value)) for quote,value in pairs)))
    wanted={clash_key(c['witness'],[(expected_by_id[r]['quote'],a) for r,a in zip(c['rules'],c['actions'])]) for c in truth['clashes']}
    found={clash_key(c['witness'],zip(c['quotes'],c['actions'])) for c in record['clashes']}
    bad_unconverted=sum(item.get('source_verified') is False for item in record['validation']['unconverted'])
    return {'rules_correctly_extracted':correct,'ground_truth_rules':sum(expected.values()),'wrong_rules':wrong,'missing_rules':missing,
            'domains_correct':domain_match,'schema_errors':len(record['validation']['errors']),'invalid_unconverted_reports':bad_unconverted,
            'clashes_found':len(found&wanted),'ground_truth_clashes':len(wanted),'missed_clashes':len(wanted-found),'false_clashes':len(found-wanted),
            'extraction_success':not(wrong or missing or not domain_match or record['validation']['errors'] or bad_unconverted)},record


def verify_manifest():
    path=CORPUS/'MANIFEST.json';manifest=json.loads(path.read_text())
    for name,expected in manifest['files'].items():
        p=ROOT/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Spec preregistration drift: '+name)
    return manifest


def evaluate(out,*,real=False):
    if real and today()!='2026-10-27':raise ValueError('The preregistered live evaluation date is 2026-10-27')
    manifest=verify_manifest();out=Path(out)
    if out.exists():raise ValueError('Evaluation output exists; do not overwrite or silently repeat')
    out.mkdir(parents=True)
    report={'kind':'real extraction evaluation' if real else 'FAKE pipeline test, not model results','status':'STARTED','entries':[],
            'manifest_sha256':hashlib.sha256((CORPUS/'MANIFEST.json').read_bytes()).hexdigest(),'completed_call_cost_usd':0,'cost_complete':True}
    def persist():(out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    persist()
    for name in manifest['order']:
        verify_manifest();doc=(CORPUS/'docs'/(name+'.md')).read_text()
        try:
            if real:proposal,cost=propose(doc)
            else:proposal=json.loads((CORPUS/'fake'/(name+'.json')).read_text())['proposal'];cost={'cost_usd':0,'model_invoked':False}
            truth=json.loads((CORPUS/'truth'/(name+'.json')).read_text())
            measured,_=score(doc,proposal,truth)
            # Rebuild a replayable review record with the actual call provenance.
            record=review(doc,proposal,lambda item:True,response_kind='real' if real else 'fake',cost=cost)
            save(record,out/name)
            report['entries'].append({'document':name,'measures':measured,'cost':cost})
            report['completed_call_cost_usd']+=cost['cost_usd'];persist()
        except (ValueError,OSError,KeyError,TypeError) as error:
            report.update(status='STOPPED',cost_complete=False,error=str(error),stopped_document=name,
                          accounting_note='All attempted real calls have durable shared results/spec-extract receipts, including unresolved reservations.')
            persist();return report
    report['status']='COMPLETE'
    counts=('rules_correctly_extracted','ground_truth_rules','wrong_rules','missing_rules','clashes_found','ground_truth_clashes','missed_clashes','false_clashes')
    report['totals']={key:sum(entry['measures'][key] for entry in report['entries']) for key in counts}
    report['totals']['successful_documents']=sum(entry['measures']['extraction_success'] for entry in report['entries'])
    report['totals']['documents']=len(manifest['order'])
    persist();return report
