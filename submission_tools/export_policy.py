"""Export diagnostics and receipt requirements, outside historical freezes."""
import json, subprocess
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from submission_tools.holdout_study import phase_failure as original_failure

def export_session(cli, session, destination, workspace, env):
    destination=Path(destination)
    stdout=destination.with_suffix('.stdout.log'); stderr=destination.with_suffix('.stderr.log')
    with stdout.open('wb') as out, stderr.open('wb') as err:
        try:
            result=subprocess.run([cli,'export','--session',session,'--out',str(destination),'--redacted'],
                cwd=workspace,env=env,stdout=out,stderr=err,timeout=20)
            code=result.returncode
        except subprocess.TimeoutExpired:
            err.write(b'\nHarness: export timeout after 20 seconds\n');code=124
        except OSError as error:
            err.write(str(error).encode());code=127
    return SimpleNamespace(returncode=code,diagnostics={'stdout_file':stdout.name,'stderr_file':stderr.name})

def phase_failure(row, results, card=False):
    # Auxiliary exports never supply primary measures. All other old stops stay.
    copy=dict(row);copy['child_exports']=[]
    error=original_failure(copy,card)
    if error:return error
    try:
        journal=json.loads((Path(results)/'raw'/row['run_id']/'provider-usage.json').read_text())
        events=[e for e in row['budget_events'] if not e.get('blocked')]
        receipts=[e for e in journal['requests'] if not e.get('blocked')]
        if not events or receipts!=events:return 'provider journal mismatch'
        totals={k:0 for k in ('input_tokens','output_tokens','cached_input_tokens')}
        for e in receipts:
            u=e['usage']
            if any(type(u[k]) is not int or u[k]<0 for k in totals) or u['cached_input_tokens']>u['input_tokens']:
                return 'invalid provider usage'
            for k in totals:totals[k]+=u[k]
        expected=(Decimal(totals['input_tokens']-totals['cached_input_tokens'])*Decimal('1.25')+Decimal(totals['cached_input_tokens'])*Decimal('.15')+Decimal(totals['output_tokens'])*Decimal('4.25'))/1000000
        if abs(expected-Decimal(str(row['cost_usd'])))>Decimal('0.000000001'):return 'provider cost mismatch'
        if row['tokens']!={'input':totals['input_tokens'],'output':totals['output_tokens'],'cached_input':totals['cached_input_tokens']}:return 'provider token mismatch'
    except (OSError,ValueError,KeyError,TypeError):return 'incomplete provider journal'
    return None


def author_command(args,*,harness=None,write_root=None,gateway_url=None):
    # Permit only this throwaway subtree inside the otherwise unreadable repo.
    from muse_guard.isolation import author_command as original
    harness=Path(harness or Path(__file__).resolve().parents[1]).resolve()
    work=Path(write_root).resolve()
    if not work.is_relative_to(harness):raise ValueError('Author workspace outside repo')
    command=original(args,harness=harness,write_root=work,gateway_url=gateway_url)
    own='(subpath '+json.dumps(str(work))+')'
    denied='(subpath '+json.dumps(str(harness))+')'
    command[2]=command[2].replace('(deny file-read* ', '(deny file-read-data ',1)
    command[2]=command[2].replace(denied,'(require-all '+denied+' (require-not '+own+'))')
    home='(subpath '+json.dumps(str(Path.home().resolve()))+')'
    command[2]=command[2].replace('(deny file-write* '+home+')','(deny file-write* (require-all '+home+' (require-not '+own+')))')
    return command

# Original candidate subprocess/check semantics, with only the own-scratch
# exception needed when scratch is beneath the otherwise denied user home.
import os,platform,signal,sys,tempfile
from muse_guard.checker import CHILD,ObservationError,CandidateExecutionError
def observe_in_repo(solution, value, *, requirements=None):
    with tempfile.TemporaryDirectory(prefix="muse-check-child-") as directory:
        isolated_solution = Path(directory) / "solution.py"
        isolated_solution.write_bytes(solution.read_bytes())
        if requirements is not None:
            # Public, approved data only. Never copy candidate-supplied rules or
            # hidden cases into the execution folder.
            (Path(directory) / "rules.yaml").write_text(json.dumps(requirements,indent=2,allow_nan=False)+"\n")
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            env = {"PATH": os.defpath, "HOME": directory, "TMPDIR": directory, "LANG": "C.UTF-8"}
            if platform.system() != "Darwin" or not Path("/usr/bin/sandbox-exec").exists():
                raise ObservationError("macOS sandbox-exec is required; unconfined execution refused")
            # Fresh policy written here; no copied Unfoolable sandbox code.
            # Read public runtime files, but explicit Seatbelt denies take
            # precedence for every user home and common secret names anywhere.
            # Candidate env contains no provider credentials; key memory remains
            # in the separate parent/gateway process (no Mach/process-info grants).
            scratch = str(Path(directory).resolve())
            home = str(Path.home().resolve())
            profile = ("(version 1)(deny default)(allow process-exec)(allow process-fork)"
                       "(allow sysctl-read)(allow file-read*)"
                       "(deny file-read* (require-all (require-any (subpath \"/Users\") (subpath \"/private/var/root\")"
                       " (subpath " + json.dumps(home) + ")) (require-not (subpath " + json.dumps(scratch) + "))))"
                       "(deny file-read* (regex #\".*[.]env([.].*)?$\")"
                       " (regex #\".*/[.](ssh|aws|config|gnupg|kube|docker|azure)(/.*)?$\")"
                       " (regex #\".*/[.](netrc|npmrc|pypirc|git-credentials|boto)$\"))"
                       "(deny file-read-data (require-all"
                       " (require-any (subpath \"/private/tmp\") (subpath \"/private/var/tmp\") (subpath \"/private/var/folders\"))"
                       " (require-not (subpath " + json.dumps(scratch) + "))))"
                       "(allow file-write* (subpath " + json.dumps(scratch) + "))")
            start_reader,start_writer=os.pipe()
            command = ["/usr/bin/sandbox-exec", "-p", profile, sys.executable, "-I", "-B", "-c", CHILD, str(isolated_solution),str(start_writer)]
            try:
                process = subprocess.Popen(command,cwd=directory,env=env,stdin=subprocess.PIPE,
                                           stdout=out,stderr=err,start_new_session=True,pass_fds=(start_writer,))
            except OSError:
                os.close(start_reader);os.close(start_writer)
                raise
            os.close(start_writer)
            timed_out=False
            try:
                process.communicate(json.dumps(value).encode(), timeout=1)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
                timed_out=True
            finally:
                # Reap same-process-group descendants even if the leader exited early.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            try:
                started=os.read(start_reader,1)==b"1"
            finally:
                os.close(start_reader)
            if not started:
                raise ObservationError("Sandbox/Python launcher could not start")
            if timed_out:
                raise CandidateExecutionError("Candidate timeout")
            if process.returncode != 0:
                raise CandidateExecutionError("Candidate process failed")
            out.seek(0)
            data = out.read(65537)
            try:
                packet = json.loads(data)
                if len(data) > 65536 or not isinstance(packet, dict) or set(packet) != {"value"}:
                    raise ValueError()
                return packet["value"]
            except (ValueError, UnicodeError, RecursionError):
                raise CandidateExecutionError("Candidate did not return one bounded JSON value") from None
