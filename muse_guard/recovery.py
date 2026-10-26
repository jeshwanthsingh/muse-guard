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

from .gateway import Gateway
from .runner import run_one, reserve_budget, ledger_records, save_total, usage_from_export
from .rules import TASKS, verify_conflict, approve, build_task, digest


RESULTS_ROOT=Path(__file__).resolve().parents[1]/"results"

def conflict_card(req,proof,results,env):
    started=time.monotonic()
    run_id="conflict-card-"+uuid.uuid4().hex[:12]
    day=datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    row={"run_id":run_id,"date":day,"stage":"day4","task":req["id"]+"-conflict-card","mode":"guarded-card",
         "pricing_mode":"STANDARD","model":"muse-spark-1.3","cost_usd":None,"tokens":None,
         "status":"PENDING","reserved_cost_usd":0.068,"model_invoked":False}
    path=results/(run_id+".json")
    reserve_budget(ledger_records(results,day),Decimal("0.068"))
    path.write_text(json.dumps(row,indent=2)+"\n")
    raw=results/"raw"/run_id;raw.mkdir(parents=True)
    try:
        with Gateway(env["META_API_KEY"],token_limit=16000,journal=raw/"provider-usage.json") as gate:
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
        path.write_text(json.dumps(row,indent=2)+"\n")
        save_total(results,day)
    return row


def choose_decision(rule_ids,decide=None,input_fn=None):
    if decide is not None:
        if decide not in rule_ids:raise ValueError("Choose one of the verified rule IDs")
        return decide,"scripted developer CLI"
    input_fn=input_fn or input
    while True:
        try:answer=input_fn("Choose "+" / ".join(rule_ids)+" (empty to stop): ").strip().upper()
        except (EOFError,KeyboardInterrupt):return None,None
        if not answer:return None,None
        if answer in rule_ids:return answer,"interactive developer CLI"
        print("Please choose a verified rule ID.")


def recover(results,decision=None,env=None,*,task_name="retry-impossible",allow_holdout=False):
    if allow_holdout and decision!="B":
        raise ValueError("Frozen holdout decision policy requires scripted B")
    env=dict(os.environ if env is None else env)
    results=Path(results).resolve();results.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    record={"recovery_id":"recovery-"+uuid.uuid4().hex[:12],"date":datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat(),
            "mode":"guarded","task":task_name,"exploratory":not allow_holdout,"study_holdout":allow_holdout,"status":"STARTED","phase_run_ids":[]}
    target=results/(record["recovery_id"]+".json")
    target.write_text(json.dumps(record,indent=2)+"\n")
    phase_rows=[]
    try:
        task=TASKS[task_name]
        record["requirements_v1"]=task["requirements"]
        record["v1_tests_hash"]=digest({"visible":task["test_source"],"hidden":task["hidden_test_source"]})
        attempt=run_one(task,results,env,mode="guarded",allow_holdout=allow_holdout)
        phase_rows.append(attempt);record["phase_run_ids"].append(attempt["run_id"])
        record["attempt"]=attempt
        if attempt["outcome"]!="CONFLICT VERIFIED":
            record["status"]=attempt["outcome"]
            return record
        report=attempt["conflict_report"]
        proof=verify_conflict(task["requirements"],report)
        record.update(witness=proof["witness"],conflict_report=report,conflict_validation=proof)
        card=conflict_card(task["requirements"],proof,results,env)
        phase_rows.append(card);record["phase_run_ids"].append(card["run_id"])
        record["conflict_card"]=card
        if card["status"]!="GENERATED":
            record["status"]="CARD GENERATION FAILED"
            return record
        print(card["text"],flush=True)
        winner,source=choose_decision(proof["rules"],decision)
        if winner is None:
            record["status"]="AWAITING DECISION"
            return record
        v2=approve(task["requirements"],winner,report,confirmed=True,source=source)
        record.update(decision=v2["approval"]["decision"],requirements_v2=v2)
        repair_task=build_task(v2)
        record["v2_tests_hash"]=digest({"visible":repair_task["test_source"],"hidden":repair_task["hidden_test_source"]})
        seed=(results/"raw"/attempt["run_id"]/"frozen"/"solution.py").read_bytes()
        repair=run_one(repair_task,results,env,seed_solution=seed,mode="guarded",allow_holdout=allow_holdout)
        phase_rows.append(repair);record["phase_run_ids"].append(repair["run_id"])
        record["repair"]=repair
        record["status"]="RECOVERED" if repair["outcome"]=="PASS" else "RECHECK DID NOT PASS"
        return record
    except (ValueError,OSError,KeyError):
        record["status"]="HARNESS ERROR"
        record["reason"]="Recovery stopped; inspect phase records, credentials or budget"
        return record
    finally:
        record["time_seconds"]=round(time.monotonic()-start,3)
        record["tokens"]={key:sum(row["tokens"][key] for row in phase_rows) for key in ("input","output","cached_input")} if all(row.get("tokens") is not None for row in phase_rows) else None
        record["cost_usd"]=float(sum((Decimal(str(row["cost_usd"])) for row in phase_rows),Decimal(0))) if all(row.get("cost_usd") is not None for row in phase_rows) else None
        target.write_text(json.dumps(record,indent=2)+"\n")


def frozen_solution(results,attempt):
    """Only consume the recorded, hash-bound candidate artifact."""
    import hashlib,re
    run_id=attempt.get("run_id","")
    if not re.fullmatch(r"[A-Za-z0-9_-]+",run_id):raise ValueError("Invalid artifact identity")
    root=Path(results).resolve()
    path=root/"raw"/run_id/"frozen"/"solution.py"
    if any(part.is_symlink() for part in (path,*path.parents) if part!=root.parent):
        raise ValueError("Artifact symlinks are forbidden")
    if not path.resolve().is_relative_to(root) or not path.is_file() or path.stat().st_size>1024*1024:
        raise ValueError("Frozen solution unavailable")
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=attempt.get("frozen_sha256",{}).get("solution.py"):
        raise ValueError("Frozen solution changed")
    return data


def resume_recovery(record_path,winner,env=None):
    """Continue a verified guarded pause. Callers cannot set the final verdict."""
    record_path=Path(record_path).resolve();results=record_path.parent
    if results!=RESULTS_ROOT.resolve():
        raise ValueError("Live continuation requires the canonical repository results ledger")
    with (results/".run.lock").open("a") as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError("Another run is active") from None
        record=json.loads(record_path.read_text())
        if record.get("status")!="AWAITING DECISION" or record.get("study_holdout"):
            raise ValueError("Only a paused development recovery can continue")
        task=TASKS[record["task"]]
        if digest(record.get("requirements_v1"))!=digest(task["requirements"]):
            raise ValueError("Recorded requirements changed")
        proof=verify_conflict(task["requirements"],record.get("conflict_report"))
        if not proof["verified"] or winner not in proof["rules"]:
            raise ValueError("A verified conflict and valid developer choice are required")
        seed=frozen_solution(results,record["attempt"])
        v2=approve(task["requirements"],winner,record["conflict_report"],confirmed=True,source="interactive developer CLI")
        record.update(status="REPAIRING",decision=v2["approval"]["decision"],requirements_v2=v2)
        record_path.write_text(json.dumps(record,indent=2)+"\n")
        started=time.monotonic()
        try:
            repair_task=build_task(v2)
            record["v2_tests_hash"]=digest({"visible":repair_task["test_source"],"hidden":repair_task["hidden_test_source"]})
            repair=run_one(repair_task,results,env,seed_solution=seed,mode="guarded")
            record["repair"]=repair;record["phase_run_ids"].append(repair["run_id"])
            record["status"]="RECOVERED" if repair["outcome"]=="PASS" else "RECHECK DID NOT PASS"
        except (ValueError,OSError,KeyError):
            record.update(status="HARNESS ERROR",reason="Live continuation stopped; inspect phase evidence")
        finally:
            rows=[record[key] for key in ("attempt","conflict_card","repair") if key in record]
            record["cost_usd"]=float(sum((Decimal(str(row["cost_usd"])) for row in rows),Decimal(0))) if all(row.get("cost_usd") is not None for row in rows) else None
            record["tokens"]={key:sum(row["tokens"][key] for row in rows) for key in ("input","output","cached_input")} if all(row.get("tokens") is not None for row in rows) else None
            record["time_seconds"]=round(record.get("time_seconds",0)+time.monotonic()-started,3)
            record_path.write_text(json.dumps(record,indent=2)+"\n")
        return record


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--decision",choices=["A","B"],help="Explicit scripted developer choice")
    parser.add_argument("--results",type=Path,default=Path("results"))
    args=parser.parse_args();args.results.mkdir(parents=True,exist_ok=True)
    with (args.results/".run.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        row=recover(args.results,args.decision)
    print(json.dumps({key:row.get(key) for key in ("recovery_id","status","witness","decision","tokens","cost_usd","time_seconds")},indent=2))


if __name__=="__main__":main()
