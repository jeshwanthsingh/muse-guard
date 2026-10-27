"""Single-use $70 study allowance, across all dates; never touches daily ledger."""
import json
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[2]
RESULTS_ROOT=ROOT/'study_runs/holdout-2026-10-27'
CAP=Decimal('70')
def ledger_records(results,day=None):
 if Path(results).resolve()!=RESULTS_ROOT.resolve():raise ValueError('Wrong study ledger')
 return [r for p in Path(results).glob('*.json') if 'run_id' in (r:=json.loads(p.read_text()))]
def reserve_budget(records,reservation):
 amount=Decimal(str(reservation))
 if not amount.is_finite() or amount<=0:raise ValueError('Invalid study reservation')
 if any(r.get('cost_usd') is None for r in records):raise ValueError('Unknown study usage; STOP')
 costs=[Decimal(str(r['cost_usd'])) for r in records]
 if any(not v.is_finite() or v<0 for v in costs):raise ValueError('Invalid study cost')
 if sum(costs,Decimal(0))+amount>CAP:raise ValueError('One-time $70 study cap exhausted')
 return reservation
def save_total(results,day=None):
 rows=ledger_records(results);known=sum((Decimal(str(r['cost_usd'])) for r in rows if r.get('cost_usd') is not None),Decimal(0))
 unknown=[r for r in rows if r.get('cost_usd') is None]
 report={'study':'holdout-2026-10-27','limit_usd':70,'separate_from_daily_cap':True,'known_cost_usd':float(known),'unknown_usage':bool(unknown),'run_count':len(rows),'can_start':not unknown and known<CAP}
 (Path(results)/'total.json').write_text(json.dumps(report,indent=2)+'\n');return report
