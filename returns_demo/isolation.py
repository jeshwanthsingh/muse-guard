"""Separate Mac sandboxes: inherited listener for service, one endpoint for checker."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import platform
import signal
import socket
import subprocess
import sys
import tempfile

LAUNCH="import runpy,sys;root=sys.argv[1];sys.path.insert(0,root);sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')"


def environment(root):
    return {'PATH':os.defpath,'HOME':str(root),'TMPDIR':str(root),'LANG':'C.UTF-8'}


def profile(root,port,role):
    root=Path(root).resolve()
    if role not in ('candidate','checker') or type(port) is not int or not 1<=port<=65535:raise ValueError('Invalid endpoint capability')
    own=json.dumps(str(root))
    policy=('(version 1)(deny default)(allow process-exec)'
            '(allow sysctl-read)(allow file-read*)'
            '(deny file-read* (require-all (require-any (subpath "/Users") (subpath "/private/var/root")'
            ' (subpath '+json.dumps(str(Path.home().resolve()))+')) (require-not (subpath '+own+'))))'
            '(deny file-read* (regex #".*[.]env([.].*)?$")'
            ' (regex #".*/[.](ssh|aws|config|gnupg|kube|docker|azure)(/.*)?$")'
            ' (regex #".*/[.](netrc|npmrc|pypirc|git-credentials|boto)$"))'
            '(deny file-read-data (require-all (require-any (subpath "/private/tmp") (subpath "/tmp")'
            ' (subpath "/private/var/tmp") (subpath "/private/var/folders"))'
            ' (require-not (subpath '+own+'))))'
            '(allow file-write* (subpath '+own+'))')
    # No candidate bind permission: listener is created and bound by the parent.
    # No outbound grant for the candidate, including other loopback endpoints.
    permission='network-inbound' if role=='candidate' else 'network-outbound'
    address='local' if role=='candidate' else 'remote'
    return policy+'(allow '+permission+' ('+address+' tcp "localhost:'+str(port)+'"))'


def command(root,port,role,script,*args):
    if platform.system()!='Darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise ValueError('Mac sandbox-exec required; unconfined execution refused')
    root=Path(root).resolve()
    if Path(script).name!=script or not (root/script).is_file():raise ValueError('Invalid sandbox script')
    return ['/usr/bin/sandbox-exec','-p',profile(root,port,role),sys.executable,'-I','-B','-c',LAUNCH,str(root),str(root/script),*map(str,args)]


def stop(process):
    if process.poll() is not None:return
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    except PermissionError:
        if process.poll() is None:process.terminate()
    try:process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        process.wait(timeout=2)


@contextmanager
def service(files):
    with tempfile.TemporaryDirectory(prefix='returns-candidate-') as directory:
        root=Path(directory).resolve()
        for name,data in files.items():
            if name not in ('server.py','refund_policy.py','test_existing.py','test_policy.py','rules.yaml','TASK.md'):raise ValueError('Unknown service artifact')
            (root/name).write_bytes(data if isinstance(data,bytes) else data.encode())
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.bind(('127.0.0.1',0));listener.listen(16)
        port=listener.getsockname()[1]
        with (root/'service.stdout.log').open('wb') as out,(root/'service.stderr.log').open('wb') as err:
            try:
                process=subprocess.Popen(command(root,port,'candidate','server.py','--socket-fd',listener.fileno()),cwd=root,
                    env=environment(root),pass_fds=(listener.fileno(),),stdout=out,stderr=err,start_new_session=True)
            finally:listener.close()
            try:yield {'root':root,'port':port,'process':process}
            finally:stop(process)


def checker_run(port,files,packet,*,timeout=15):
    with tempfile.TemporaryDirectory(prefix='returns-checker-') as directory:
        root=Path(directory).resolve()
        for name,data in files.items():
            if '/' in name or name not in ('check_driver.py','test_existing.py','probe.py'):raise ValueError('Unknown checker artifact')
            (root/name).write_bytes(data if isinstance(data,bytes) else data.encode())
        script='probe.py' if 'probe.py' in files else 'check_driver.py'
        result=subprocess.run(command(root,port,'checker',script,str(port)),cwd=root,env=environment(root),
            input=json.dumps(packet),capture_output=True,text=True,timeout=timeout,start_new_session=True)
        if len(result.stdout)>1024*1024 or len(result.stderr)>65536:raise ValueError('Oversized checker output')
        if result.returncode:raise ValueError('Checker process failed (exit '+str(result.returncode)+')')
        return json.loads(result.stdout)
