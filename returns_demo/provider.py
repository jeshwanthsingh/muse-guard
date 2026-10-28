"""Opt-in next-day calls: shared $5 daily ledger and complete provider receipts."""
from contextlib import contextmanager
from contextvars import ContextVar
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import time
import urllib.request
import uuid
from spec_guard.provider import today,PROMPT
from muse_guard.runner import ledger_records,reserve_budget,save_total,usage_from_export
from submission_tools.settlement import ReconciledGateway
from returns_demo.source import ROOT

REAL_DATE='2026-10-29'
RESULTS=ROOT/'results'
MODEL='muse-spark-1.3'
RUN_ID=ContextVar('returns_service_run_id',default=None)


def require_real_date():
    if today()!=REAL_DATE:raise ValueError('No paid calls today; this one-run command is reserved for '+REAL_DATE)


@contextmanager
def phase(kind,max_tokens):
    require_real_date()
    if RUN_ID.get() is None:raise ValueError('Service run identity required before paid calls')
    key=os.environ.get('META_API_KEY') or os.environ.get('MODEL_API_KEY')
    if not key:raise ValueError('Set the provider key in the trusted parent environment')
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        prior=ledger_records(RESULTS,today())
        if any(r.get('cost_usd') is None for r in prior):raise ValueError('Unknown prior provider usage; stop')
        allowance=Decimal(max_tokens)*Decimal('4.25')/1000000
        reserve_budget(prior,allowance)
        identity='returns-'+kind+'-'+uuid.uuid4().hex[:12]
        row={'run_id':identity,'service_run_id':RUN_ID.get(),'date':today(),'stage':'returns-service demo, outside evaluation','model':MODEL,
             'pricing_mode':'STANDARD','cost_basis':'provider usage at configured Standard token rates','max_tokens':max_tokens,'cost_usd':None,
             'accounted_upper_bound_usd':float(allowance),'model_invoked':False}
        path=RESULTS/(identity+'.json');path.write_text(json.dumps(row,indent=2)+'\n');started=time.monotonic()
        gate=None
        try:
            with ReconciledGateway(key,token_limit=max_tokens,dollar_limit=allowance,journal=RESULTS/'raw'/identity/'provider-usage.json') as gate:
                yield gate,row
        finally:
            events=gate.events if gate is not None else []
            calls=[e for e in events if not e.get('blocked')]
            row.update(model_invoked=bool(calls),provider_calls=len(calls),budget_events=events,time_seconds=round(time.monotonic()-started,3))
            if not calls:row.update(cost_usd=0,tokens={'input':0,'output':0,'cached_input':0})
            elif all(e.get('usage') is not None for e in calls):
                measured={k:sum(e['usage'][k] for e in calls) for k in ('input_tokens','output_tokens','cached_input_tokens')}
                row['tokens'],row['cost_usd']=usage_from_export({'usage':measured})
            if row['cost_usd'] is not None:row.pop('accounted_upper_bound_usd',None)
            path.write_text(json.dumps(row,indent=2)+'\n');save_total(RESULTS,today())


def propose(doc):
    with phase('extract',6144) as (gate,receipt):
        request=urllib.request.Request(gate.url+'/responses',data=json.dumps({'model':MODEL,'instructions':PROMPT,
            'input':doc,'max_output_tokens':2048,'reasoning':{'effort':'minimal'},'store':False}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=130) as response:packet=json.load(response)
        (RESULTS/'raw'/receipt['run_id']/'response.json').write_text(json.dumps(packet,indent=2)+'\n')
    if receipt['cost_usd'] is None:raise ValueError('Unknown extraction usage; stop')
    if packet.get('status')!='completed':raise ValueError('Spark did not complete extraction; no retry')
    text=''.join(p.get('text','') for item in packet.get('output',[]) if item.get('type')=='message' for p in item.get('content',[]) if p.get('type')=='output_text')
    try:proposal=json.loads(text)
    except ValueError:raise ValueError('Spark extraction was not JSON; no retry') from None
    return proposal,receipt
