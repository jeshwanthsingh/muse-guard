# Derived unchanged card prompt/protocol; separate study ledger and corrected gateway.
"""One exploratory, fully recorded conflict -> decision -> repair flow."""
import argparse
from datetime import datetime
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import time
import urllib.request
import uuid
from zoneinfo import ZoneInfo

from submission_tools.settlement import ReconciledGateway as Gateway
from submission_tools.export_runtime.runner import run_one, reserve_budget, ledger_records, save_total, usage_from_export
from muse_guard.rules import TASKS, verify_conflict, approve, build_task, digest


from submission_tools.export_runtime.ledger import RESULTS_ROOT, CAP

def is_recovered(repair):
    return repair.get('outcome')=='PASS'

def conflict_card(req,proof,results,env,*,dollar_quota=False):
    started=time.monotonic()
    run_id="conflict-card-"+uuid.uuid4().hex[:12]
    day=datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    row={"run_id":run_id,"date":day,"stage":"holdout-study","task":req["id"]+"-conflict-card","mode":"guarded-card",
         "pricing_mode":"STANDARD","model":"muse-spark-1.3","cost_usd":None,"tokens":None,
         "status":"PENDING","reserved_cost_usd":0.068,"model_invoked":False}
    path=results/(run_id+".json")
    allowance=Decimal('0.068')
    if dollar_quota:
        prior=ledger_records(results,day);reserve_budget(prior,Decimal('0.00000001'))
        spent=sum((Decimal(str(r['cost_usd'] if r.get('cost_usd') is not None else r['accounted_upper_bound_usd'])) for r in prior),Decimal(0))
        allowance=min(allowance,CAP-spent)
    reserve_budget(ledger_records(results,day),allowance)
    row['reserved_cost_usd']=float(allowance)
    path.write_text(json.dumps(row,indent=2)+"\n")
    raw=results/"raw"/run_id;raw.mkdir(parents=True)
    try:
        with Gateway(env["META_API_KEY"],token_limit=16000,journal=raw/"provider-usage.json",dollar_limit=allowance if dollar_quota else None) as gate:
            facts={"rules":req["rules"],"witness":proof["witness"],"actions":proof["actions"]}
            prompt=("Write a short plain-English conflict card for a developer from these independently verified facts. "
                    "Explain the concrete input, name both rules and the incompatible actions, and ask which rule wins. "
                    "Do not claim code is verified. Do not decide priority. Text only. Facts: "+json.dumps(facts))
            request=urllib.request.Request(gate.url+"/responses",data=json.dumps({"model":"muse-spark-1.3",
                "input":prompt,"max_output_tokens":1024,"reasoning":{"effort":"low"},"store":False}).encode(),
                headers={"Content-Type":"application/json"})
            try:
                with urllib.request.urlopen(request,timeout=150) as response:
                    packet=json.load(response)
                (raw/"response.json").write_text(json.dumps(packet))
                text="\n".join(part.get("text","") for item in packet.get("output",[]) if item.get("type")=="message"
                               for part in item.get("content",[]) if part.get("type")=="output_text")
                if not text.strip():
                    raise ValueError("No conflict card text returned")
                row.update(status="GENERATED",text=text,advisory_only=True)
            finally:
                gate.stop()
                admissions=[event for event in gate.events if not event.get("blocked")]
                row["model_invoked"]=bool(admissions)
                row["budget_events"]=gate.events
                row["budget_stop"]=any(e.get("blocked") and e.get("block_kind")=="budget" for e in gate.events)
                if admissions and all(event.get("usage") is not None for event in admissions):
                    usage={key:sum(event["usage"][key] for event in admissions)
                           for key in ("input_tokens","output_tokens","cached_input_tokens")}
                    row["tokens"],row["cost_usd"]=usage_from_export({"usage":usage})
                elif not admissions:
                    row.update(tokens={"input":0,"output":0,"cached_input":0},cost_usd=0)
    except (ValueError,OSError,KeyError):
        row["status"]="HARNESS ERROR"
    finally:
        row["time_seconds"]=round(time.monotonic()-started,3)
        row["cost_basis"]="all terminal provider usage, persisted from first request"
        if row.get('cost_usd') is None:row['accounted_upper_bound_usd']=float(allowance)
        path.write_text(json.dumps(row,indent=2)+"\n")
        save_total(results,day)
    return row
