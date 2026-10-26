"""Custom confirmed-spec adapter. Does not register or mutate study catalog tasks."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from .core import load_confirmed,space
from .provider import budgeted
from muse_guard.rules import build_task,digest
from muse_guard.tasks import materialize,prompt
from muse_guard.rule_checker import check_rules
from muse_guard.runner import run_process,freeze,final_claim
from muse_guard.isolation import author_command


def make_task(table):
    inputs=space(table['input_space'])
    if len(inputs)<2:raise ValueError('At least two finite inputs required for separate visible/hidden checks')
    req=copy.deepcopy(table)
    req['approval']={'source':'task author','content_hash':digest(req)}
    return build_task(req,samples={'visible_inputs':inputs[::2],'hidden_inputs':inputs[1::2],'split':'spec'})


def run_confirmed(path,*,candidate=None,real=False,out):
    table,record=load_confirmed(path);out=Path(out)
    if out.exists():raise ValueError('Run output already exists')
    if record['validation']['errors']:raise ValueError('Invalid source table; conversion must be corrected')
    if record['clashes']:
        result={'outcome':'CONFLICT VERIFIED','clashes':record['clashes'],'model_invoked':False,'cost_usd':0,'reason':'Clashes found before coding; review the source spec first'}
    elif record['uncovered_inputs']:raise ValueError('Uncovered inputs have no confirmed fallback; coding refused')
    else:
        task=make_task(table)
        with tempfile.TemporaryDirectory(prefix='muse-spec-author-') as directory:
            root=Path(directory);workspace=root/'agent';materialize(task,workspace)
            if candidate:
                source=Path(candidate)
                if source.is_symlink() or not source.is_file() or source.stat().st_size>1024*1024:raise ValueError('Invalid candidate source')
                (workspace/'solution.py').write_bytes(source.read_bytes())
                result=check_rules(task,workspace)
                result.update(model_invoked=False,cost_usd=0,source='supplied candidate; no model call')
            else:
                if not real:raise ValueError('Choose --candidate solution.py for offline checks or explicitly --real')
                cli=shutil.which('muse')
                if not cli:raise ValueError('Muse Code CLI unavailable')
                for name in ('home','config','tmp'):(root/name).mkdir()
                clean={'PATH':os.defpath+':/opt/homebrew/bin:/usr/local/bin','HOME':str(root/'home'),'TMPDIR':str(root/'tmp'),
                       'XDG_CONFIG_HOME':str(root/'config'),'LANG':'C.UTF-8','MUSE_NO_AUTO_UPDATE':'1','MUSE_CONTRIBUTOR_MODE':'0'}
                session=str(uuid.uuid4())
                with budgeted('code',max_tokens=320000) as (gate,cost):
                    args=[cli,'exec','--api-key-stdin','--provider','meta','--model','muse-spark-1.3','--base-url',gate.url,
                          '--preset','miniswe','--reasoning-effort','low','--max-model-steps','12','--max-tool-output-bytes','4096',
                          '--no-foreign-personal-context','--disable-web-tools','--approval-judge','off','--disable-approval',
                          '--disable-sandbox','--workspace',str(workspace),'--session-id',session,'--json',prompt(task)]
                    executed=run_process(author_command(args,write_root=root,gateway_url=gate.url),workspace,clean,timeout=300,input_data=b'proxy-only-no-provider-key\n')
                freeze(workspace,root/'frozen')
                result=check_rules(task,root/'frozen',final_claim(executed.stdout))
                result.update(cost,exit_code=executed.returncode)
            result.update(kind='confirmed spec coding check; outside study',confirmed_sha256=record['confirmed_sha256'])
    out.mkdir(parents=True);(out/'run.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
