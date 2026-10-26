"""Save display-only observations before starting a viewer. No model calls."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from muse_guard.view import load_record
from muse_guard.recovery import frozen_solution
from muse_guard.evidence import session_evidence
from muse_guard.quality_gate import input_space
from muse_guard.checker import _observe,ObservationError,CandidateExecutionError

ROOT=Path(__file__).resolve().parents[1];RESULTS=ROOT/'results'

def prepare(path):
 row=load_record(path);req=row['requirements_v1'];witness=row['conflict_validation']['witness']
 attempt=row['attempt'];repair=row['repair']
 frozen_solution(RESULTS,attempt);frozen_solution(RESULTS,repair)
 source=RESULTS/'raw'/attempt['run_id']/'session.json'
 if source.is_symlink() or source.stat().st_size>4*1024*1024:raise ValueError('Invalid export')
 message=session_evidence(json.loads(source.read_text()))['agent_message']
 if not message:raise ValueError('Actual agent message unavailable')
 candidates=[x for x in input_space(req) if x!=witness]
 candidates.sort(key=lambda x:sum(type(x[k]) is not type(witness[k]) or x[k]!=witness[k] for k in witness))
 values=[witness]+candidates[:3];observations=[]
 for value in values:
  observed={'input':value,'witness':value==witness}
  for label,phase in [('before',attempt),('after',repair)]:
   frozen_solution(RESULTS,phase) # refuse altered solution bytes
   folder=RESULTS/'raw'/phase['run_id']/'frozen';rules=folder/'rules.yaml'
   if rules.is_symlink() or hashlib.sha256(rules.read_bytes()).hexdigest()!=phase['frozen_sha256']['rules.yaml']:
    raise ValueError('Frozen rules changed')
   try:observed[label]=_observe(folder/'solution.py',value,requirements=json.loads(rules.read_text()))
   except CandidateExecutionError:observed[label]='Candidate failed'
   except ObservationError:observed[label]='Observation unavailable'
  observations.append(observed)
 row['source_record']=row['recovery_id'];row['recovery_id']+='-view-day5'
 row['display_evidence']={'agent_message':message,'agent_message_sha256':hashlib.sha256(message.encode()).hexdigest(),
  'message_source':'muse export: assistant_message_committed','source_export_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'behavior':observations,'behavior_source':'sandboxed candidate processes; actual frozen rules; no verdict mutation',
  'before_solution_sha256':attempt['frozen_sha256']['solution.py'],'after_solution_sha256':repair['frozen_sha256']['solution.py']}
 target=RESULTS/(row['recovery_id']+'.json');target.write_text(json.dumps(row,indent=2)+'\n')
 print(target.name);return target

if __name__=='__main__':prepare(Path(sys.argv[1]))
