"""Deterministic source linkage, developer review, and finite-domain clash search."""
import copy
import hashlib
import itertools
import json
import math
import re

UNSPECIFIED='__UNSPECIFIED__'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def sentences(doc):
    # Full nonempty punctuation-delimited sentences/lines, preserving exact bytes.
    chunks=re.split(r'(?<=[.!?])\s+|\n+',doc)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def space(domains):
    return [dict(zip(domains,values)) for values in itertools.product(*domains.values())]


def domain_errors(domains):
    if not isinstance(domains,dict) or not 1<=len(domains)<=6:return ['Expected 1–6 finite input fields']
    errors=[];count=1
    for field,values in domains.items():
        if not isinstance(field,str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,31}',field):errors.append('Invalid field name')
        if not isinstance(values,list) or not 1<=len(values)<=8:
            errors.append('Missing or oversized finite domain for '+str(field));continue
        count*=len(values)
        if any(type(v) not in (bool,int,float,str) or (isinstance(v,float) and not math.isfinite(v)) or (isinstance(v,str) and len(v)>64) for v in values):
            errors.append('Domain values must be small finite primitives');continue
        if len({json.dumps(v,allow_nan=False) for v in values})!=len(values):errors.append('Duplicate domain value')
    if count>256:errors.append('Input space exceeds 256 combinations')
    return errors


def matches(rule,value):
    for field,condition in rule['when'].items():
        actual=value[field]
        for op,wanted in condition.items():
            if op=='eq' and (type(actual) is not type(wanted) or actual!=wanted):return False
            if op=='gte' and actual<wanted:return False
    return True


def validate(doc,proposal):
    units=sentences(doc);items=[];errors=[]
    if not isinstance(proposal,dict):proposal={};errors.append('Model response must be a JSON object')
    if set(proposal)-{'input_space','rules','default','unconverted'}:errors.append('Unexpected proposal fields')
    domains=proposal.get('input_space');errors+=domain_errors(domains)
    rules=proposal.get('rules')
    if not isinstance(rules,list):errors.append('rules must be a list');rules=[]
    if len(rules)>16:errors.append('At most 16 rules are supported')
    ids=[r.get('id') for r in rules if isinstance(r,dict)]
    for index,raw in enumerate(rules):
        issues=list(errors);rule=raw if isinstance(raw,dict) else {}
        if not isinstance(raw,dict) or set(rule)!={'id','quote','when','action'}:issues.append('Expected id, quote, when, action only')
        identity=rule.get('id')
        if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}',identity) or identity=='DEFAULT':issues.append('Invalid or reserved rule ID')
        if ids.count(identity)!=1:issues.append('Duplicate rule ID')
        quote=rule.get('quote')
        if not isinstance(quote,str) or quote not in units:issues.append('Quote is not an exact full source sentence')
        action=rule.get('action')
        if not isinstance(action,str) or not 1<=len(action)<=64:issues.append('Action must be a short string')
        when=rule.get('when')
        if not isinstance(when,dict) or not when:issues.append('Missing condition')
        elif not errors:
            for field,ops in when.items():
                if field not in domains:issues.append('Missing field domain: '+field);continue
                if not isinstance(ops,dict) or not ops or set(ops)-{'eq','gte'}:issues.append('Only eq/gte conditions are supported');continue
                for op,wanted in ops.items():
                    if op=='eq' and not any(type(wanted) is type(v) and wanted==v for v in domains[field]):issues.append('Condition value outside field domain')
                    if op=='gte' and (type(wanted) not in (int,float) or not math.isfinite(wanted) or any(type(v) not in (int,float) for v in domains[field])):issues.append('gte requires a finite numeric domain and threshold')
        if not issues and not any(matches(rule,value) for value in space(domains)):issues.append('Rule cannot match any declared input')
        items.append({'key':'rule-'+str(index+1),'kind':'rule','proposal':copy.deepcopy(raw),'errors':issues,'valid':not issues})
    if 'default' in proposal:
        default=proposal['default'];issues=list(errors)
        if not isinstance(default,dict) or set(default)!={'quote','action'}:issues.append('Default requires quote and action')
        else:
            if default['quote'] not in units:issues.append('Default quote is not an exact source sentence')
            if not isinstance(default['action'],str) or not 1<=len(default['action'])<=64:issues.append('Invalid default action')
        items.append({'key':'default','kind':'default','proposal':copy.deepcopy(default),'errors':issues,'valid':not issues})
    proposed_quotes={i['proposal'].get('quote') for i in items if isinstance(i['proposal'],dict) and isinstance(i['proposal'].get('quote'),str)}
    unconverted=[]
    for unit in units:
        if unit not in proposed_quotes:unconverted.append({'quote':unit,'reason':'No rule proposed for this sentence; review whether context or a missing requirement'})
    reported=proposal.get('unconverted',[])
    if not isinstance(reported,list):errors.append('unconverted must be a list');reported=[reported]
    for item in reported:
        unconverted.append({'quote':item.get('quote','') if isinstance(item,dict) else '',
            'reason':item.get('reason','Model could not convert') if isinstance(item,dict) else 'Malformed unconverted item',
            'source_verified':isinstance(item,dict) and item.get('quote') in units})
    # A top-level schema error discovered late invalidates all proposed rows.
    if errors:
        for item in items:item['errors']=list(dict.fromkeys(item['errors']+errors));item['valid']=False
    return {'input_space':copy.deepcopy(domains) if isinstance(domains,dict) else {},'items':items,'errors':errors,'unconverted':unconverted}


def clashes(table):
    found=[]
    for value in space(table['input_space']):
        matching=[r for r in table['rules'] if matches(r,value)]
        for a,b in itertools.combinations(matching,2):
            if a['action']!=b['action']:found.append({'verified':True,'witness':value,'rules':[a['id'],b['id']],
                'actions':[a['action'],b['action']],'quotes':[a['quote'],b['quote']]})
    return found


def review(doc,proposal,decide,*,model='muse-spark-1.3',response_kind='fake',cost=None):
    try:json.dumps(proposal,allow_nan=False)
    except ValueError:proposal={'invalid_response':json.dumps(proposal)}
    validated=validate(doc,proposal);decisions=[];rules=[];default=None
    for item in validated['items']:
        accepted=bool(decide(item)) if item['valid'] else False
        decisions.append({'key':item['key'],'decision':'confirmed' if accepted else 'rejected' if item['valid'] else "couldn't convert"})
        if accepted:
            if item['kind']=='default':default=copy.deepcopy(item['proposal'])
            else:
                rule=copy.deepcopy(item['proposal']);rule['text']=rule['quote'];rules.append(rule)
    doc_hash=hashlib.sha256(doc.encode()).hexdigest()
    table={'id':'spec-'+doc_hash[:12],'pair':'spec-'+doc_hash[:12],'version':1,'input_space':validated['input_space'],
           'default':default['action'] if default else UNSPECIFIED,'rules':rules,'default_source':default,
           'spec_origin':{'doc_sha256':doc_hash,'model':model,'response_kind':response_kind}}
    found=clashes(table) if not domain_errors(table['input_space']) else []
    uncovered=[x for x in space(table['input_space']) if not any(matches(r,x) for r in rules)] if not domain_errors(table['input_space']) and default is None else []
    record={'schema':1,'kind':'spec review','doc':doc,'doc_sha256':doc_hash,'model':model,'response_kind':response_kind,
            'proposal':proposal,'proposal_sha256':digest(proposal),'validation':validated,'decisions':decisions,
            'confirmed':table,'confirmed_sha256':digest(table),'clashes':found,'uncovered_inputs':uncovered,'cost':cost or {'cost_usd':0,'model_invoked':False}}
    return record


def load_confirmed(path):
    from pathlib import Path
    table=json.loads(Path(path).read_text());record_path=Path(path).with_name('record.json')
    record=json.loads(record_path.read_text())
    replay=review(record['doc'],record['proposal'],lambda i:next(d['decision'] for d in record['decisions'] if d['key']==i['key'])=='confirmed',
                  model=record['model'],response_kind=record['response_kind'],cost=record['cost'])
    if record!=replay or table!=record['confirmed'] or digest(table)!=record['confirmed_sha256']:
        raise ValueError('Confirmed table or review receipt changed')
    return table,record
