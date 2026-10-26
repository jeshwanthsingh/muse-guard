"""Explicit future dev pilot. Importing or summarizing this module never calls models."""
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from .metrics import summarize,checker_inventory

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'study/clean_pilot_plan.json'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_day(plan,day=None):
    day=day or datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
    if day!=plan['scheduled_date']:raise ValueError('Clean pilot is scheduled for '+plan['scheduled_date']+'; no execution on '+day)


def validate_plan(plan):
    wanted={(p+'-'+kind,kind,mode,1) for p in ('retry','refund','shipping') for kind in ('solvable','impossible') for mode in ('plain','guarded')}
    observed=[(e['task'],e['kind'],e['mode'],e['repeat']) for e in plan['entries']]
    if len(observed)!=12 or set(observed)!=wanted or plan['daily_limit_usd']!=5 or (plan['max_model_steps'],plan['max_tokens'],plan['timeout_seconds'])!=(12,320000,300):
        raise ValueError('Only the preregistered balanced dev allocation and limits are allowed')


def freeze_ready(entries):
    if len(entries)!=12:return False
    for entry in entries:
        record=entry.get('record')
        if not record or record.get('status') in {'STARTED','HARNESS ERROR','CARD GENERATION FAILED','AWAITING DECISION'}:return False
        attempt=record.get('attempt')
        if not attempt:return False
        for name in ('attempt','repair','conflict_card'):
            row=record.get(name)
            if row is None:continue
            if row.get('cost_usd') is None or row.get('authoring_infrastructure_error') or row.get('outcome')=='HARNESS ERROR':return False
            if row.get('budget_stop') or any(e.get('blocked') and e.get('block_kind')!='shutdown' for e in row.get('budget_events',[])):return False
            if name!='conflict_card':
                if not row.get('model_invoked') or type(row.get('main_steps')) is not int or row['main_steps']<1:return False
                if row.get('cli_version')!='Muse Code 1.4.2 (1.4.2-R4684.1)':return False
                if row.get('outcome') not in {'CONFLICT REPORTED','CONFLICT VERIFIED'} and not checker_inventory(row):return False
            if any(not e.get('blocked') and e.get('usage') is None for e in row.get('budget_events',[])):return False
    return True


def source_hashes():
    from .freeze import LOCKED_FILES
    return {name:sha(ROOT/name) for name in LOCKED_FILES}


def load_entries(path):
    cohort=json.loads(Path(path).read_text());plan=json.loads(PLAN.read_text());validate_plan(plan)
    if cohort.get('schema')!=1 or cohort.get('plan_sha256')!=sha(PLAN) or len(cohort.get('entries',[]))!=12:
        raise ValueError('Pilot does not match the preregistration')
    entries=[]
    for actual,expected in zip(cohort['entries'],plan['entries']):
        if any(actual.get(k)!=v for k,v in expected.items()):raise ValueError('Pilot assignment order changed')
        item=dict(expected,record=None);identity=actual.get('record_id')
        if identity:
            if not re.fullmatch(r'[A-Za-z0-9_-]+',identity):raise ValueError('Invalid record ID')
            record_path=ROOT/'results'/(identity+'.json')
            if record_path.is_symlink() or sha(record_path)!=actual.get('record_sha256'):raise ValueError('Pilot record changed')
            item['record']=json.loads(record_path.read_text())
            for key in ('attempt','repair','conflict_card'):
                phase=item['record'].get(key)
                if phase is None:continue
                phase_id=phase['run_id']
                if not re.fullmatch(r'[A-Za-z0-9_-]+',phase_id):raise ValueError('Invalid phase ID')
                target=ROOT/'results'/(phase_id+'.json')
                if target.is_symlink() or sha(target)!=actual['phase_sha256'].get(phase_id) or json.loads(target.read_text())!=phase:
                    raise ValueError('Phase evidence changed')
        entries.append(item)
    return cohort,entries


def summary(path):
    cohort,entries=load_entries(path)
    return {'pilot_date':cohort['date'],'preregistration':'docs/PRIMARY_MEASURES.md','valid_for_refreeze':freeze_ready(entries),
            'study_results':False,'holdout_model_calls':0,'primary_results':summarize(entries)}


def execute():
    plan=json.loads(PLAN.read_text());validate_plan(plan);validate_day(plan)
    if not os.environ.get('META_API_KEY'):raise ValueError('Supply the key through the execution environment')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('Commit the final reviewed code before the clean pilot')
    from .runner import ledger_records,reserve_budget,save_total
    from .plain import recover_plain
    from .recovery import recover
    results=ROOT/'results';target=results/('CLEAN_PILOT_'+plan['scheduled_date']+'.json')
    with (results/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if target.exists():raise ValueError('This pilot already has evidence; never overwrite or silently repeat it')
        reserve_budget(ledger_records(results,plan['scheduled_date']),Decimal('1.36'))
        pinned=source_hashes()
        cohort={'schema':1,'date':plan['scheduled_date'],'plan_sha256':sha(PLAN),'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'source_hashes':pinned,'status':'STARTED','holdout_model_calls':0,'entries':[dict(e,record_id=None,stop_reason='not started') for e in plan['entries']]}
        target.write_text(json.dumps(cohort,indent=2)+'\n')
        try:
            for entry in cohort['entries']:
                total=save_total(results,plan['scheduled_date'])
                if not total['can_start'] or source_hashes()!=pinned:
                    entry['stop_reason']='daily cap/unknown usage or source drift';continue
                row=(recover_plain(results,task_name=entry['task'],decision='B',dollar_quota=True) if entry['mode']=='plain' else
                     recover(results,'B',task_name=entry['task'],dollar_quota=True))
                entry.update(record_id=row['recovery_id'],record_sha256=sha(results/(row['recovery_id']+'.json')),
                    phase_sha256={name:sha(results/(name+'.json')) for name in row['phase_run_ids']},stop_reason=None)
                target.write_text(json.dumps(cohort,indent=2)+'\n');print(entry['task'],entry['mode'],row['status'],row.get('cost_usd'),flush=True)
            cohort['status']='FINISHED'
        finally:
            cohort['ledger']=save_total(results,plan['scheduled_date']);target.write_text(json.dumps(cohort,indent=2)+'\n')
    return target
