"""One spec -> decision -> approved implementation -> independent recheck record.
Uses existing validator, approval, test generator, sandbox and checker unchanged.
"""
import copy,hashlib,json,os,shutil,tempfile,uuid,subprocess
from pathlib import Path
from spec_guard.core import review,space,domain_errors
from spec_guard.cli import decision
from spec_guard.provider import propose,budgeted
from muse_guard.rules import approve,build_task,digest,content,normalized
from muse_guard.tasks import materialize,prompt
from muse_guard.runner import run_process,freeze,final_claim
from muse_guard.isolation import author_command
from muse_guard.rule_checker import check_rules
from submission_tools.behavior_score import score
from submission_tools.baseten import child_environment

FAKE='constructed fake Spark and Muse responses; not observed model behavior'

def task_for(req):
 values=space(req['input_space'])
 if len(values)<2:raise ValueError('At least two inputs are needed for visible and hidden checks')
 return build_task(req,samples={'visible_inputs':values[::2],'hidden_inputs':values[1::2],'split':'spec'})

def reviewed_requirements(spec):
 req=copy.deepcopy(spec['confirmed']);mapping={r['id']:normalized(r['id']) for r in req['rules']}
 if len(set(mapping.values()))!=len(mapping):raise ValueError('Rule IDs collide after normalization')
 for rule in req['rules']:rule['id']=mapping[rule['id']]
 req['source_rule_ids']=mapping
 req['approval']={'source':'task author','content_hash':digest(req)}
 return req

def approve_decision(req,clashes,choice,*,scripted=False):
 order=[normalized(x) for x in choice.split(',')]
 first=next((c for c in clashes if order[0] in [normalized(x) for x in c['rules']]),None)
 if first is None:raise ValueError('Top-priority rule must participate in a displayed conflict')
 report={'conflict':True,'rules':[normalized(x) for x in first['rules']],'witness':first['witness'],'explanation':'Exhaustively verified conflicting actions in the confirmed table'}
 order=[normalized(x) for x in choice.split(',')];known=[r['id'] for r in req['rules']]
 if len(known)==2 and len(order)==1:order += [x for x in known if x not in order]
 if len(order)!=len(known) or set(order)!=set(known):raise ValueError('Explicitly order every rule ID, highest priority first')
 # Existing approval machinery binds v1, the witness and the developer decision.
 winner=next(x for x in order if x in report['rules'])
 result=approve(req,winner,report,confirmed=True,source='scripted developer CLI' if scripted else 'interactive developer CLI')
 # Existing approval validation requires the witness winner to be first. For a
 # multi-rule table choose a witness involving the first-ranked rule, or refuse.
 if order[0]!=winner:raise ValueError('Top-priority rule must participate in the displayed conflict; review a smaller table')
 result['priority']=order;result['decision'].update(priority_order=order,scope='Developer-approved total rule order; first matching rule chooses the one next action')
 result['approval']['decision']=copy.deepcopy(result['decision']);result['approval']['content_hash']=digest(content(result))
 return result

def recheck(task,workspace,claim):
 original=workspace/'test_original.py';rules=workspace/'rules.yaml';solution=workspace/'solution.py'
 if any(p.is_symlink() for p in (original,rules,solution)):raise ValueError('Candidate symlinks refused')
 if not solution.is_file() or solution.stat().st_size>1024*1024:raise ValueError('Candidate source unavailable or oversized')
 if any(p.exists() and p.stat().st_size>1024*1024 for p in (original,rules)):raise ValueError('Candidate artifact oversized')
 edited=not original.exists() or original.read_text()!=task['test_source']
 runtime=json.loads(rules.read_text()) if rules.exists() else {}
 # Restore trusted tests outside the agent folder. Agent edits are descriptive.
 with tempfile.TemporaryDirectory(prefix='continuous-check-') as directory:
  scratch=Path(directory)/'candidate';materialize(task,scratch);(scratch/'solution.py').write_bytes(solution.read_bytes())
  result=check_rules(task,scratch,claim,runtime_requirements=runtime)
 result.update(expected_test_ids=task['expected_names'],original_tests_edited=edited,
               agent_rules_changed=runtime!=task['requirements'],test_edits_are_descriptive=True)
 result['behavior_score']=score(result,task['requirements'])
 return result

def implement(task,*,fake=None):
 with tempfile.TemporaryDirectory(prefix='continuous-agent-') as directory:
  root=Path(directory);workspace=root/'agent';materialize(task,workspace)
  before=(workspace/'solution.py').read_text()
  if fake is not None:
   files=fake['files']
   if set(files)-{'solution.py','test_original.py','rules.yaml'}:raise ValueError('Unknown fake artifact')
   for name,text in files.items():
    if not isinstance(text,str) or len(text.encode())>1024*1024:raise ValueError('Invalid fake artifact')
    (workspace/name).write_text(text)
   claim=fake.get('claim','');cost={'model_invoked':False,'cost_usd':0};exit_code=None
  else:
   cli=shutil.which('muse')
   if not cli:raise ValueError('Muse Code CLI unavailable')
   for name in ('home','tmp','config'):(root/name).mkdir()
   with budgeted('continuous-code',max_tokens=320000) as (gate,cost):
    args=[cli,'exec','--api-key-stdin','--provider','meta','--model','muse-spark-1.3','--base-url',gate.url,
          '--preset','miniswe','--reasoning-effort','low','--max-model-steps','12','--max-tool-output-bytes','4096',
          '--no-foreign-personal-context','--disable-web-tools','--approval-judge','off','--disable-approval','--disable-sandbox',
          '--workspace',str(workspace),'--session-id',str(uuid.uuid4()),'--json',prompt(task)]
    completed=run_process(author_command(args,write_root=root,gateway_url=gate.url),workspace,child_environment(root),timeout=300,input_data=b'proxy-only-no-provider-key\n')
   claim=final_claim(completed.stdout);exit_code=completed.returncode
  freeze(workspace,root/'frozen');checked=recheck(task,root/'frozen',claim)
  import difflib
  after=(root/'frozen/solution.py').read_text()
  return {'checks':checked,'cost':cost,'exit_code':exit_code,'claim':claim,'solution_sha256':hashlib.sha256(after.encode()).hexdigest(),
          'diff':''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/solution.py',tofile='after/solution.py'))}

def run(doc,out,*,fake_packet=None,accept_all=False,choice=None,reviewer=None):
 from submission_tools.continuous_view import render
 out=Path(out)
 if out.exists():raise ValueError('Choose a new output folder; evidence is never overwritten')
 if not doc.strip() or len(doc.encode())>16384:raise ValueError('Requirements must be nonempty and at most 16 KiB')
 if fake_packet is not None and fake_packet.get('kind')!=FAKE:raise ValueError('Fake response must be explicitly labeled')
 record={'schema':1,'kind':'continuous spec recovery','response_kind':'fake' if fake_packet is not None else 'real',
         'model':'muse-spark-1.3','status':'EXTRACTING','doc_sha256':hashlib.sha256(doc.encode()).hexdigest(),
         'study':False,'stages':[],'cost_usd':0 if fake_packet is not None else None}
 out.mkdir(parents=True)
 def save():
  (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
  if 'spec' in record:(out/'index.html').write_text(render(record))
 save()
 try:
  if fake_packet is not None:proposal=fake_packet['proposal'];extract_cost={'model_invoked':False,'cost_usd':0}
  else:proposal,extract_cost=propose(doc)
  record['extraction_cost']=extract_cost
  spec=review(doc,proposal,reviewer or (lambda i:decision(i,accept_all=accept_all)),response_kind=record['response_kind'],cost=extract_cost)
  record.update(spec=spec,status='REVIEWED');record['stages'].append('rules reviewed');save()
  for item in spec['validation']['unconverted']:print('NOT CONVERTED:',item['quote'])
  for item,reviewed in zip(spec['validation']['items'],spec['decisions']):
   if reviewed['decision']!='confirmed':print(reviewed['decision'].upper()+':',json.dumps(item['proposal']))
  if spec['validation']['errors'] or domain_errors(spec['confirmed']['input_space']):raise ValueError('Invalid declared input space or proposal schema')
  if spec['uncovered_inputs']:raise ValueError('Uncovered inputs require an explicitly confirmed fallback')
  req=reviewed_requirements(spec);record['requirements_v1']=req
  if spec['clashes']:
   record.update(status='AWAITING DECISION');save()
   for clash in spec['clashes']:print('VERIFIED CLASH:',json.dumps(clash))
   scripted=choice is not None
   if choice is None:choice=input('Choose rule priority (e.g. B for two rules, or B,A,C): ').strip()
   req=approve_decision(req,spec['clashes'],choice,scripted=scripted)
   record.update(requirements_v2=req,decision=req['decision']);record['stages'].append('developer decision approved')
  task=task_for(req);record.update(status='IMPLEMENTING',declared_input_count=len(space(req['input_space'])))
  (out/'approved.yaml').write_text(json.dumps(req,indent=2)+'\n');save()
  result=implement(task,fake=fake_packet['implementation'] if fake_packet is not None else None)
  record['implementation']=result;record['stages'].extend(['Muse implementation' if fake_packet is None else 'fake Muse implementation','independent recheck'])
  scored=result['checks']['behavior_score'];record.update(status='CHECKED',outcome=scored['outcome'])
  count=len(result['checks']['tests']) if scored['evidence_complete'] else 0
  record['checked_input_count']=count
  values=space(req['input_space']);record['check_inputs']=task['visible_cases']+task['hidden_cases']
  costs=[extract_cost.get('cost_usd'),result['cost'].get('cost_usd')]
  record['cost_usd']=sum(costs) if all(x is not None for x in costs) else None
 except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
  record.update(status='ERROR',error='Muse timed out; shared usage receipt retained' if isinstance(error,subprocess.TimeoutExpired) else str(error));save();raise ValueError(record['error']) from None
 save();return record
