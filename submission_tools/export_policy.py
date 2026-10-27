"""Export diagnostics and receipt requirements, outside historical freezes."""
import json, subprocess
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from submission_tools.holdout_study import phase_failure as original_failure

def export_session(cli, session, destination, workspace, env):
    destination=Path(destination)
    stdout=destination.with_suffix('.stdout.log'); stderr=destination.with_suffix('.stderr.log')
    with stdout.open('wb') as out, stderr.open('wb') as err:
        try:
            result=subprocess.run([cli,'export','--session',session,'--out',str(destination),'--redacted'],
                cwd=workspace,env=env,stdout=out,stderr=err,timeout=20)
            code=result.returncode
        except subprocess.TimeoutExpired:
            err.write(b'\nHarness: export timeout after 20 seconds\n');code=124
        except OSError as error:
            err.write(str(error).encode());code=127
    return SimpleNamespace(returncode=code,diagnostics={'stdout_file':stdout.name,'stderr_file':stderr.name})

def phase_failure(row, results, card=False):
    # Auxiliary exports never supply primary measures. All other old stops stay.
    copy=dict(row);copy['child_exports']=[]
    error=original_failure(copy,card)
    if error:return error
    try:
        journal=json.loads((Path(results)/'raw'/row['run_id']/'provider-usage.json').read_text())
        events=[e for e in row['budget_events'] if not e.get('blocked')]
        receipts=[e for e in journal['requests'] if not e.get('blocked')]
        if not events or receipts!=events:return 'provider journal mismatch'
        totals={k:0 for k in ('input_tokens','output_tokens','cached_input_tokens')}
        for e in receipts:
            u=e['usage']
            if any(type(u[k]) is not int or u[k]<0 for k in totals) or u['cached_input_tokens']>u['input_tokens']:
                return 'invalid provider usage'
            for k in totals:totals[k]+=u[k]
        expected=(Decimal(totals['input_tokens']-totals['cached_input_tokens'])*Decimal('1.25')+Decimal(totals['cached_input_tokens'])*Decimal('.15')+Decimal(totals['output_tokens'])*Decimal('4.25'))/1000000
        if abs(expected-Decimal(str(row['cost_usd'])))>Decimal('0.000000001'):return 'provider cost mismatch'
        if row['tokens']!={'input':totals['input_tokens'],'output':totals['output_tokens'],'cached_input':totals['cached_input_tokens']}:return 'provider token mismatch'
    except (OSError,ValueError,KeyError,TypeError):return 'incomplete provider journal'
    return None
