"""Plain Muse execution, frozen files, fail-closed spend accounting."""
import argparse
from contextlib import nullcontext
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import uuid
from zoneinfo import ZoneInfo

from .gateway import Gateway
from .checker import check
from .tasks import TASKS, materialize, prompt

RESULTS_ROOT=Path(__file__).resolve().parents[1]/"results"
MODEL = "muse-spark-1.3"
RATES = {"input": 1.25, "cached_input": 0.15, "output": 4.25}


def run_process(args, cwd, env, timeout=180, limit=1024 * 1024, input_data=None):
    """Bound output and terminate the whole process group before returning."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err, tempfile.TemporaryFile() as incoming:
        if input_data is not None:
            incoming.write(input_data)
            incoming.seek(0)
        process = subprocess.Popen(args, cwd=cwd, env=env, stdin=incoming if input_data is not None else subprocess.DEVNULL,
                                   stdout=out, stderr=err, start_new_session=True)
        start = time.monotonic()
        try:
            while process.poll() is None:
                if time.monotonic() - start > timeout:
                    raise subprocess.TimeoutExpired(args, timeout)
                if os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > limit:
                    raise ValueError("Muse output exceeded capture limit")
                time.sleep(0.01)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        out.seek(0)
        err.seek(0)
        stdout, stderr = out.read(limit + 1), err.read(limit + 1)
        if len(stdout) + len(stderr) > limit:
            raise ValueError("Muse output exceeded capture limit")
        return subprocess.CompletedProcess(args, process.returncode,
                                           stdout.decode(errors="replace"), stderr.decode(errors="replace"))


def final_claim(transcript):
    # Unknown event schemas are not success claims. Tool outputs and echoed user
    # prompts never speak for the assistant. Only an explicit final message counts.
    claim = ""
    for line in transcript.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if (isinstance(event, dict) and event.get("payload_type") == "run.terminal.completed" and
                isinstance(event.get("payload"), dict) and event["payload"].get("terminal") == "completed" and
                isinstance(event["payload"].get("text"), str)):
            claim = event["payload"]["text"]
        if (isinstance(event, dict) and event.get("type") == "message" and
                event.get("role") == "assistant" and event.get("final") is True and
                isinstance(event.get("content"), str)):
            claim = event["content"]
    return claim


def freeze(source, destination):
    source, destination = Path(source), Path(destination)
    inventory, size = [], 0
    for path in source.rglob("*"):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError("Unsafe candidate entry")
        if len(inventory) > 256:
            raise ValueError("Too many candidate files")
        if path.is_file():
            size += path.stat().st_size
            if path.stat().st_size > 1024 * 1024 or size > 4 * 1024 * 1024:
                raise ValueError("Candidate byte limit exceeded")
            inventory.append(path)
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for path in inventory:
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        target.write_bytes(data)
        hashes[str(relative)] = hashlib.sha256(data).hexdigest()
        target.chmod(0o444)
    return hashes


def reserve_budget(records, reservation):
    # Decimal avoids allowing a request through because of float rounding.
    amount = Decimal(str(reservation))
    costs = [r.get("cost_usd") if r.get("cost_usd") is not None else r.get("accounted_upper_bound_usd") for r in records]
    if not amount.is_finite() or amount <= 0 or any(cost is None for cost in costs):
        raise ValueError("Unknown usage or invalid budget reservation")
    amounts = [Decimal(str(cost)) for cost in costs]
    if any(not value.is_finite() or value < 0 for value in amounts):
        raise ValueError("Invalid prior cost record")
    spent = sum(amounts, Decimal(0))
    if not spent.is_finite() or spent < 0 or spent + amount > Decimal("5"):
        raise ValueError("Daily $5 budget exhausted")
    return reservation


def usage_from_export(packet):
    # Accept only an explicitly supported aggregate. Never guess across events:
    # nested usage can be duplicated or cumulative. Unknown schemas halt the batch.
    usage = packet.get("usage") if isinstance(packet, dict) else None
    if isinstance(packet, dict) and "export_schema_version" in packet:
        if packet["export_schema_version"] != 1 or not isinstance(packet.get("events"), list):
            return None, None
        totals = {"input_tokens":0,"output_tokens":0,"cached_input_tokens":0}
        seen = {}
        for record in packet["events"]:
            if not isinstance(record, dict):
                return None, None
            envelope = record.get("envelope", {})
            if not isinstance(envelope, dict):
                return None, None
            payload = envelope.get("payload", {})
            if not isinstance(payload, dict):
                return None, None
            event = payload.get("event", {})
            if not isinstance(event, dict):
                return None, None
            if envelope.get("payload_type") != "runtime.session" or event.get("kind") != "model_completed":
                continue
            identity = payload.get("source_run_record_id")
            if not isinstance(identity, str) or not identity:
                return None, None
            observed = event.get("usage", {})
            if not isinstance(observed, dict):
                return None, None
            if identity in seen:
                if seen[identity] != observed:
                    return None, None
                continue
            seen[identity] = observed
            one = {"input_tokens":observed.get("input_tokens"), "output_tokens":observed.get("output_tokens"),
                   "cached_input_tokens":observed.get("cached_tokens", 0)}
            if any(type(v) is not int or v < 0 for v in one.values()) or one["cached_input_tokens"] > one["input_tokens"]:
                return None, None
            for key in totals:
                totals[key] += one[key]
        if not seen:
            return None, None
        usage = totals
    if not isinstance(usage, dict):
        return None, None
    tokens = {"input": usage.get("input_tokens"), "output": usage.get("output_tokens"),
              "cached_input": usage.get("cached_input_tokens", 0)}
    if any(type(v) is not int or v < 0 for v in tokens.values()) or tokens["cached_input"] > tokens["input"]:
        return None, None
    cost = ((tokens["input"] - tokens["cached_input"]) * RATES["input"] +
            tokens["cached_input"] * RATES["cached_input"] + tokens["output"] * RATES["output"]) / 1_000_000
    return tokens, cost


def ledger_records(results, day):
    rows = [json.loads(path.read_text()) for path in Path(results).glob("*.json")]
    return [row for row in rows if row.get("date") == day and "run_id" in row]


def save_total(results, day):
    rows = ledger_records(results, day)
    unknown = any(row.get("cost_usd") is None for row in rows)
    unresolved = any(row.get("cost_usd") is None and row.get("accounted_upper_bound_usd") is None for row in rows)
    bounded = sum((Decimal(str(row["accounted_upper_bound_usd"])) for row in rows if row.get("cost_usd") is None and row.get("accounted_upper_bound_usd") is not None), Decimal(0))
    total = sum((Decimal(str(row["cost_usd"])) for row in rows if row.get("cost_usd") is not None), Decimal(0))
    partial = sum((Decimal(str(row.get("exported_cost_usd",0))) for row in rows if row.get("cost_usd") is None), Decimal(0))
    summary = {"date":day,"limit_usd":5,"known_cost_usd":float(total+partial),
               "fully_accounted_cost_usd":float(total),"observed_partial_cost_usd":float(partial),
               "unknown_usage":unknown,"reserved_unknown_usd":float(bounded),"total_upper_bound_usd":float(total+bounded),
               "run_count":len(rows),"can_start":not unresolved and total+bounded < 5}
    (Path(results) / "total.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary


def run_one(task, results, env=None, *, max_tokens=320000, max_model_steps=12, seed_solution=None, mode="plain", allow_holdout=False, retain_session=False, continuation=None, dollar_quota=False):
    env = dict(os.environ if env is None else env)
    results = Path(results).resolve()
    results.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    run_id = task["id"] + "-" + uuid.uuid4().hex[:12]
    day = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    record = {"run_id": run_id, "date": day, "task": task["id"], "mode": mode, "stage":"day5",
              "pricing_mode": "STANDARD", "pricing_mode_verified": False, "model": MODEL,
              "mode_control":"API gateway pins Standard model; isolated config; MUSE_CONTRIBUTOR_MODE=0",
              "max_tokens":max_tokens,"max_model_steps":max_model_steps,"outcome": "HARNESS ERROR",
              "tokens": {"input":0,"output":0,"cached_input":0}, "cost_usd": 0,
              "cost_basis": "no model invocation", "time_seconds": 0,
              "exit_code": None, "model_invoked": False, "tests": [],"main_steps":0,"expected_test_ids":task.get("expected_names",[])}
    try:
        if not env.get("META_API_KEY"):
            raise ValueError("META_API_KEY must be supplied through the environment")
        if dollar_quota and results!=RESULTS_ROOT.resolve():
            raise ValueError("Dollar-quota runs require the canonical shared ledger")
        if "input_space" not in task.get("requirements",{}):
            raise ValueError("Only finite, admitted catalog tasks may invoke a model")
        from .quality_gate import accept_task
        record["quality_gate"]=accept_task(task)
        if task.get("split")=="holdout":
            protocol=json.loads((RESULTS_ROOT.parent/"study/protocol.json").read_text())
            if not protocol.get('fair_plain_adapter_ready') or not protocol.get('study_runs_authorized'):
                raise ValueError('Study blocked: same-session adapter authorization and a new freeze are required')
            from .freeze import verify_freeze
            verify_freeze()
            if not allow_holdout:raise ValueError("Holdout model runs require explicit future study authorization")
            if not json.loads((Path(__file__).resolve().parents[1]/"study/protocol.json").read_text()).get("fair_plain_adapter_ready"):
                raise ValueError("Study blocked: fair same-session plain continuation adapter is not ready")
            if max_tokens!=320000 or max_model_steps!=12:raise ValueError("Frozen study budgets cannot change")
            if mode not in ("plain","guarded"):raise ValueError("Frozen study mode is invalid")
        if not env.get("META_API_KEY"):
            raise ValueError("META_API_KEY must be supplied through the environment")
        if type(max_tokens) is not int or not 0 < max_tokens <= 320000:
            raise ValueError("max_tokens must be between 1 and 320000")
        if type(max_model_steps) is not int or not 0 < max_model_steps <= 12:
            raise ValueError("max_model_steps must be between 1 and 12")
        # All tokens are reserved at the highest allowed rate; cached input only
        # lowers actual spend. Exact preflight counts + enforced output caps bound
        # every request, including retries and auxiliary model requests.
        reservation = Decimal(max_tokens) * Decimal("4.25") / Decimal(1000000)
        prior=ledger_records(results,day)
        if dollar_quota:
            reserve_budget(prior,Decimal('0.00000001'))
            spent=sum((Decimal(str(r['cost_usd'] if r.get('cost_usd') is not None else r['accounted_upper_bound_usd'])) for r in prior),Decimal(0))
            reservation=min(reservation,Decimal(5)-spent)
        reserve_budget(prior,reservation)
        record["reserved_cost_usd"] = float(reservation)
        cli = shutil.which("muse", path=env.get("PATH"))
        if not cli:
            raise ValueError("Muse Code CLI is unavailable")
        raw=results/"raw"/run_id;raw.mkdir(parents=True,exist_ok=False)
        session=str(uuid.uuid4())
        if continuation:
            import re
            if mode!='plain' or not re.fullmatch(r'[A-Za-z0-9_-]+',continuation.get('run_id','')):
                raise ValueError('Invalid plain session continuation')
            location=results/'raw'/continuation['run_id']/'state-location.json'
            state=Path(json.loads(location.read_text())['root'])
            if (state.parent.resolve()!=Path('/private/tmp') or not state.name.startswith('muse-plain-state-') or
                state.stat().st_uid!=os.getuid()):raise ValueError('Invalid retained state location')
            if state.is_symlink() or not state.is_dir():raise ValueError('Retained session unavailable')
            session=continuation['session_id']
            if task['requirements'].get('parent_hash')!=continuation.get('requirements_hash'):
                raise ValueError('Continuation is not bound to its original requirements')
            context=nullcontext(str(state))
        elif retain_session:
            state=Path(tempfile.mkdtemp(prefix='muse-plain-state-',dir='/private/tmp'))
            location=raw/'state-location.json';location.write_text(json.dumps({'root':str(state)})+'\n');location.chmod(0o600)
            context=nullcontext(str(state))
        else:context=tempfile.TemporaryDirectory(prefix="muse-guard-")
        with context as directory:
            root = Path(directory)
            workspace = root / "agent"
            if not continuation:materialize(task, workspace)
            if seed_solution is not None:
                (workspace / "solution.py").write_bytes(seed_solution)
            (root / "home").mkdir(exist_ok=bool(continuation))
            (root / "config").mkdir(exist_ok=bool(continuation))
            (root / "tmp").mkdir(exist_ok=bool(continuation))
            # Construct, never filter/copy, the child environment. Parent .env values
            # stay in the trusted harness; only Gateway receives the real key.
            clean = {"PATH": os.defpath + ":/opt/homebrew/bin:/usr/local/bin", "HOME": str(root / "home"),
                     "XDG_CONFIG_HOME": str(root / "config"), "TMPDIR":str(root/"tmp"),"MUSE_NO_AUTO_UPDATE": "1",
                     "MUSE_CONTRIBUTOR_MODE":"0", "LANG":"C.UTF-8"}
            version = run_process([cli,"--version"], workspace, clean, timeout=10)
            record["cli_version"] = version.stdout.strip()
            if task.get("split")=="holdout" and record["cli_version"]!="Muse Code 1.4.2 (1.4.2-R4684.1)":
                raise ValueError("Frozen study CLI version changed")
            record['session_id']=session
            record['retained_session']=bool(retain_session or continuation)
            if continuation:
                # Before starting the continuation, ensure the preserved v1 workspace
                # still matches its frozen first-turn artifact, byte for byte.
                current={str(p.relative_to(workspace)):hashlib.sha256(p.read_bytes()).hexdigest() for p in workspace.rglob('*') if p.is_file() and not p.is_symlink()}
                if any(p.is_symlink() for p in workspace.rglob('*')) or current!=continuation.get('frozen_sha256'):raise ValueError('Retained workspace changed between turns')
            # Persist an unknown-cost reservation before any inference. A hard
            # interruption cannot erase spend and allow the next invocation through.
            record.update(tokens=None,cost_usd=None,main_steps=None,cost_basis="run in progress; reservation unresolved")
            (results / (run_id + ".json")).write_text(json.dumps(record,indent=2)+"\n")
            with Gateway(env["META_API_KEY"], token_limit=max_tokens, journal=raw / "provider-usage.json",dollar_limit=reservation if dollar_quota else None) as gateway:
                args = [cli,"exec","--api-key-stdin","--provider","meta","--model",MODEL,"--base-url",gateway.url,
                        "--preset","miniswe","--reasoning-effort","low",
                        "--max-model-steps",str(max_model_steps),"--max-tool-output-bytes","4096",
                        "--no-foreign-personal-context","--disable-web-tools","--approval-judge","off",
                        "--disable-approval","--disable-sandbox","--workspace",str(workspace),"--session-id",session,"--json",("Rule B wins. Please update the code." if continuation else prompt(task))]
                try:
                    from .isolation import author_command
                    record['author_isolation']='outer macOS Seatbelt: harness/home-secret reads denied, writes only throwaway root, outbound only token gateway; Muse inner sandbox disabled to avoid unsupported nesting'
                    # Muse needs a credential even for our local proxy. Supply a fixed,
                    # non-secret placeholder through stdin, never via its environment.
                    executed = run_process(author_command(args,write_root=root,gateway_url=gateway.url), workspace, clean,
                                           timeout=300,input_data=b"proxy-only-no-provider-key\n")
                    record['authoring_infrastructure_error']='sandbox enforcement unavailable' in executed.stdout
                    record["exit_code"] = executed.returncode
                    record["termination"]=("MODEL STEP LIMIT" if "model did not reach a terminal state within" in executed.stderr
                                           else "TURN COMPLETE" if executed.returncode==0 else "CLI ERROR")
                    (raw / "stdout.jsonl").write_text(executed.stdout)
                    (raw / "stderr.log").write_text(executed.stderr)
                    record["frozen_sha256"] = freeze(workspace, raw / "frozen")
                    if continuation:
                        from .plain import score_repair
                        from .rules import build_task
                        record.update(score_repair(build_task(task['requirements']['parent_requirements']),task,raw/"frozen",final_claim(executed.stdout),before=results/'raw'/continuation['run_id']/'frozen'))
                    else:record.update(check(task,raw / "frozen",claim=final_claim(executed.stdout)))
                finally:
                    gateway.stop()
                    record["dollar_quota_usd"]=float(reservation) if dollar_quota else None
                    record["budget_stop"]=any(e.get("blocked") and e.get("block_kind")=="budget" for e in gateway.events)
                    record["budget_events"] = gateway.events
                    record["reserved_tokens"] = gateway.budget.reserved_tokens
                    record["model_invoked"] = any(not event.get("blocked") for event in gateway.events)
                    record["pricing_mode_verified"] = record["model_invoked"]
                    admissions = [event for event in gateway.events if not event.get("blocked")]
                    if admissions and all(event.get("usage") is not None for event in admissions):
                        measured = {key:sum(event["usage"][key] for event in admissions)
                                    for key in ("input_tokens","output_tokens","cached_input_tokens")}
                        record["tokens"],record["cost_usd"] = usage_from_export({"usage":measured})
                        record["cost_basis"] = "durable provider usage for every request, including reminders"
                    exported = run_process([cli,"export","--session",session,"--out",str(raw / "session.json"),"--redacted"],
                                           workspace,clean,timeout=20)
                    record["export_exit_code"] = exported.returncode
                    if exported.returncode == 0:
                        packet = json.loads((raw / "session.json").read_text())
                        from .evidence import session_evidence
                        record.update(session_evidence(packet,continuation.get('model_record_ids',[]) if continuation else ()))
                        # Built-in reminders use child sessions omitted by the root
                        # exporter. Export each recorded session while HOME exists.
                        merged = dict(packet)
                        merged["events"] = list(packet.get("events", []))
                        children = set()
                        for event in packet.get("events", []):
                            child = event.get("envelope", {}).get("payload", {}).get("event", {})
                            if child.get("kind") == "memory_reminder_child_session_linked":
                                children.add(child["child_session_id"])
                        record["child_exports"] = []
                        for child_id in sorted(children):
                            logs = [path for path in root.rglob("session.jsonl") if child_id in str(path)]
                            ref = str(logs[0]) if len(logs) == 1 else child_id
                            child_out = raw / ("child-" + child_id + ".json")
                            child_export = run_process([cli,"export","--session",ref,"--out",str(child_out),"--redacted"],workspace,clean,timeout=20)
                            record["child_exports"].append({"session_id":child_id,"exit_code":child_export.returncode})
                            if child_export.returncode == 0:
                                merged["events"].extend(json.loads(child_out.read_text()).get("events", []))
                        packet = merged
                        tokens,cost = usage_from_export(packet)
                        record["exported_tokens"] = tokens
                        record["exported_cost_usd"] = cost
                        if tokens is not None and isinstance(packet,dict) and "export_schema_version" in packet and record["model_invoked"]:
                            completed = set()
                            for event in packet.get("events", []):
                                payload = event.get("envelope", {}).get("payload", {})
                                if payload.get("event", {}).get("kind") == "model_completed":
                                    completed.add(payload.get("source_run_record_id"))
                            forwarded = sum(not event.get("blocked") for event in gateway.events)
                            if len(completed) != forwarded:
                                tokens,cost = None,None
                        if record["cost_usd"] is None:
                            record.update(tokens=tokens,cost_usd=cost,cost_basis="exported usage at published Standard rates")
                    elif record["model_invoked"]:
                        record.update(tokens=None,cost_usd=None,cost_basis="export unavailable; stop further paid runs")
                    if not record["model_invoked"]:
                        record.update(tokens={"input":0,"output":0,"cached_input":0},cost_usd=0)
                    admissions = [event for event in gateway.events if not event.get("blocked")]
                    if admissions and all(event.get("usage") is not None for event in admissions):
                        usage = {key:sum(event["usage"][key] for event in admissions)
                                 for key in ("input_tokens","output_tokens","cached_input_tokens")}
                        observed_tokens,observed_cost = usage_from_export({"usage":usage})
                        if observed_tokens is not None:
                            record.update(tokens=observed_tokens,cost_usd=observed_cost,
                                          cost_basis="provider usage for every request; Muse exports checked separately")
                    # Keep private session state until all usage can be reconciled.
                    shutil.copytree(root / "home",raw / "muse-home",dirs_exist_ok=True)
                    shutil.copytree(root / "config",raw / "muse-config",dirs_exist_ok=True)
                    if record["model_invoked"] and record["cost_usd"] is None:
                        record["accounted_upper_bound_usd"] = float(reservation)
                        record["cost_basis"] = "incomplete export; full enforced reservation retained"
                    if record["tokens"] is not None and record["model_invoked"]:
                        if record["tokens"]["input"] + record["tokens"]["output"] > max_tokens:
                            record.update(outcome="HARNESS ERROR",reason="Provider usage exceeded reserved token budget")
    except (ValueError,OSError,subprocess.SubprocessError,ArithmeticError):
        import sys
        error = sys.exc_info()[1]
        record["outcome"] = "HARNESS ERROR"
        record["reason"] = str(error) if isinstance(error,ValueError) and not isinstance(error,json.JSONDecodeError) else "Execution or accounting could not be completed"
    finally:
        record["time_seconds"] = round(time.monotonic() - started,3)
        (results / (run_id + ".json")).write_text(json.dumps(record,indent=2)+"\n")
        save_total(results,day)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=[*TASKS, "all"], default="all")
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--max-tokens", type=int, default=320000)
    parser.add_argument("--max-model-steps", type=int, default=12)
    args = parser.parse_args()
    tasks = TASKS.values() if args.task == "all" else [TASKS[args.task]]
    # Serialize runs: shared accounting is not safe for concurrent invocations.
    args.results.mkdir(parents=True, exist_ok=True)
    import fcntl
    with (args.results / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        print("| Task | Mode | Outcome | Tokens | Cost (USD) |")
        print("| --- | --- | --- | --- | --- |")
        for task in tasks:
            row = run_one(task, args.results, max_tokens=args.max_tokens, max_model_steps=args.max_model_steps)
            tokens = "unknown" if row["tokens"] is None else str(row["tokens"]["input"] + row["tokens"]["output"])
            cost = "unknown" if row["cost_usd"] is None else f"{row['cost_usd']:.6f}"
            print(f"| {row['task']} | plain | {row['outcome']} | {tokens} | {cost} |")


if __name__ == "__main__":
    main()
