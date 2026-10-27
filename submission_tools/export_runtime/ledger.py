"""Dev smoke uses shared daily ledger; restart is disabled pending a new freeze."""
from decimal import Decimal
from pathlib import Path
from muse_guard.runner import ledger_records,save_total
from muse_guard.runner import reserve_budget as daily_reserve
from submission_tools.holdout_study import verify_freeze
ROOT=Path(__file__).resolve().parents[2]
RESULTS_ROOT=ROOT/'results'
CAP=Decimal('5')
def reserve_budget(records,reservation):
    if any(r.get('cost_usd') is None for r in records):raise ValueError('Unknown usage; STOP')
    return daily_reserve(records,reservation)
def authorize(task,allow_holdout):
    verify_freeze()
    if task.get('split')!='dev' or allow_holdout:raise ValueError('DEV smoke only; no holdout authorization')
    return {'stage':'export-amendment-dev-smoke','study_id':None}
