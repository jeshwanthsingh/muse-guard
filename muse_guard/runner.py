"""Plain Muse execution, frozen files, fail-closed spend accounting."""
import argparse
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

from .checker import check
from .tasks import TASKS, materialize, prompt

MODEL = "muse-spark-1.3"
RATES = {"input": 1.25, "cached_input": 0.15, "output": 4.25}


def run_process(args, cwd, env, timeout=180, limit=1024 * 1024):
    """Bound output and terminate the whole process group before returning."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        process = subprocess.Popen(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
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
    if not amount.is_finite() or amount <= 0 or any(r.get("cost_usd") is None for r in records):
        raise ValueError("Unknown usage or invalid budget reservation")
    spent = sum((Decimal(str(r["cost_usd"])) for r in records), Decimal(0))
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


def run_one(task, results, env=None):
    env = dict(os.environ if env is None else env)
    results = Path(results).resolve()
    results.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    run_id = task["id"] + "-" + uuid.uuid4().hex[:12]
    day = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    record = {"run_id": run_id, "date": day, "task": task["id"], "mode": "plain",
              "pricing_mode": "STANDARD", "pricing_mode_verified": False, "model": MODEL, "outcome": "ERROR", "tokens": {"input":0,"output":0,"cached_input":0},
              "cost_usd": 0, "cost_basis": "no model invocation", "time_seconds": 0,
              "exit_code": None, "model_invoked": False, "tests": []}
    try:
        if not env.get("META_API_KEY"):
            raise ValueError("META_API_KEY must be supplied through the environment")
        # CLI step caps cannot enforce a dollar ceiling. Require the user to first
        # enforce an isolated key/team daily cap in Meta billing, then attest here.
        cap = Decimal(env.get("MUSE_GUARD_DAILY_LIMIT_USD", "0"))
        if not cap.is_finite() or not 0 < cap <= 5 or env.get("MUSE_GUARD_STANDARD_CONFIRMED") != "1":
            raise ValueError("Confirm Standard mode and an enforced Meta daily limit of at most $5")
        cli = shutil.which("muse", path=env.get("PATH"))
        if not cli:
            raise ValueError("Muse Code CLI is unavailable")
        existing = [json.loads(path.read_text()) for path in results.glob("*.json")]
        today = [row for row in existing if row.get("date") == day]
        if any(row.get("cost_usd") is None for row in today):
            raise ValueError("Unknown prior usage blocks further model calls")
        spent = sum((Decimal(str(row["cost_usd"])) for row in today), Decimal(0))
        remaining = cap - spent
        reserve_budget(today, remaining)
        with tempfile.TemporaryDirectory(prefix="muse-guard-") as directory:
            root = Path(directory)
            workspace = root / "agent"
            materialize(task, workspace)
            (root / "home").mkdir()
            (root / "config").mkdir()
            clean = {"PATH": env.get("PATH", os.defpath), "HOME": str(root / "home"),
                     "XDG_CONFIG_HOME": str(root / "config"), "MUSE_NO_AUTO_UPDATE": "1",
                     "META_API_KEY": env["META_API_KEY"], "LANG": "C.UTF-8"}
            version = run_process([cli, "--version"], workspace, clean, timeout=10)
            record["cli_version"] = version.stdout.strip()
            help_result = run_process([cli, "exec", "--help"], workspace, clean, timeout=10)
            if "--contributor-mode" not in help_result.stdout:
                raise ValueError("Installed Muse CLI lacks documented --contributor-mode off; live run blocked")
            raw = results / "raw" / run_id
            raw.mkdir(parents=True, exist_ok=False)
            session = str(uuid.uuid4())
            args = [cli, "exec", "--provider", "meta", "--model", MODEL, "--contributor-mode", "off",
                    "--max-model-steps", "6", "--max-tool-output-bytes", "4096", "--no-foreign-personal-context",
                    "--disable-web-tools", "--approval-judge", "off", "--disable-approval",
                    "--workspace", str(workspace), "--session-id", session, "--json", prompt(task)]
            # Until invocation, no token usage can accrue. After invocation, unknown
            # usage reserves the rest of the day and prevents any further run.
            record.update(model_invoked=True, pricing_mode_verified=True, tokens=None, cost_usd=None, cost_basis="usage not yet observed")
            executed = run_process(args, workspace, clean, timeout=180)
            record["exit_code"] = executed.returncode
            (raw / "stdout.jsonl").write_text(executed.stdout)
            (raw / "stderr.log").write_text(executed.stderr)
            record["frozen_sha256"] = freeze(workspace, raw / "frozen")
            record.update(check(task, raw / "frozen", claim=final_claim(executed.stdout)))
            exported = run_process([cli, "export", "--session", session, "--out", str(raw / "session.json"), "--redacted"],
                                   workspace, clean, timeout=20)
            record["export_exit_code"] = exported.returncode
            if exported.returncode == 0:
                tokens, cost = usage_from_export(json.loads((raw / "session.json").read_text()))
                record.update(tokens=tokens, cost_usd=cost, cost_basis="estimated from published Standard rates and exported usage" if cost is not None else "unsupported export usage schema")
    except (ValueError, OSError, subprocess.SubprocessError, ArithmeticError):
        # Keep errors portable and credential-free; exception text may include CLI
        # output, filesystem paths, or provider credentials.
        import sys
        error = sys.exc_info()[1]
        record["outcome"] = "ERROR"
        record["reason"] = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else "Execution or accounting could not be completed"
    finally:
        record["time_seconds"] = round(time.monotonic() - started, 3)
        (results / (run_id + ".json")).write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=[*TASKS, "all"], default="all")
    parser.add_argument("--results", type=Path, default=Path("results"))
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
            row = run_one(task, args.results)
            tokens = "unknown" if row["tokens"] is None else str(row["tokens"]["input"] + row["tokens"]["output"])
            cost = "unknown" if row["cost_usd"] is None else f"{row['cost_usd']:.6f}"
            print(f"| {row['task']} | plain | {row['outcome']} | {tokens} | {cost} |")


if __name__ == "__main__":
    main()
