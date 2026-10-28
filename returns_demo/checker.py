"""Reference expectations and pristine HTTP checks stay outside the agent folder."""
import hashlib
from pathlib import Path
from returns_demo.source import baseline_files
from returns_demo.isolation import service,checker_run
from muse_guard.rules import actions,approved

REGRESSIONS=('test_health','test_create_and_get','test_unique_ids','test_invalid_fields','test_unknown_routes','test_evaluation_persists','test_evaluate_rejects_payload')
INPUTS=[{'eligible':True,'fraud_hold':True},{'eligible':True,'fraud_hold':False},
        {'eligible':False,'fraud_hold':False},{'eligible':False,'fraud_hold':True}]


def check(files,requirements=None):
    if requirements is not None and (requirements.get('version')!=2 or not approved(requirements) or any(len(actions(requirements,x))!=1 for x in INPUTS)):
        raise ValueError('Approved conflict-free v2 required for changed policy expectations')
    # This interpreter is only the independent reference answer, never candidate code.
    cases=[{'input':value,'expected':actions(requirements,value)[0] if requirements else 'refund_immediately' if value['eligible'] else 'reject'} for value in INPUTS]
    expected=['policy.test_case_'+str(i) for i in range(4)]+['regression.'+name for name in REGRESSIONS]
    trusted={'check_driver.py':Path(__file__).with_name('check_driver.py').read_bytes(),'test_existing.py':baseline_files()['test_existing.py']}
    with service(files) as candidate:
        result=checker_run(candidate['port'],trusted,{'cases':cases,'expected_test_ids':expected},timeout=30)
    rows=result.get('tests',[]);ids=[r.get('id') for r in rows]
    inventory=(len(ids)==len(expected) and len(ids)==len(set(ids)) and set(ids)==set(expected) and all(r.get('status') in ('PASS','FAIL','ERROR') for r in rows))
    result['inventory_complete']=inventory
    if not inventory:result['outcome']='HARNESS ERROR'
    else:result['outcome']='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL'
    for row in rows:
        row['layer']='hidden policy' if row['id']=='policy.test_case_3' else 'visible policy' if row['id'].startswith('policy.') else 'existing regression'
    result.update(cases=cases,expected_test_ids=expected,regression_source_sha256=hashlib.sha256(trusted['test_existing.py']).hexdigest(),
                  channel='parent-owned IPv4 loopback listener; checker pins its port; no redirects or candidate outbound network')
    return result
