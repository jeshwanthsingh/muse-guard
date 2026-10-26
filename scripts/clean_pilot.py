"""Tomorrow's explicit dev-only pilot; --plan and --summary are offline."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from muse_guard.pilot import PLAN,execute,summary
p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
mode.add_argument('--plan',action='store_true');mode.add_argument('--execute',action='store_true');mode.add_argument('--summary',type=Path)
a=p.parse_args()
try:
 if a.plan:print(PLAN.read_text())
 elif a.summary:print(json.dumps(summary(a.summary),indent=2))
 else:print(execute())
except (ValueError,OSError,KeyError) as error:p.exit(2,str(error)+'\n')
