"""No provider calls: verify endpoint restrictions with actual denied operations."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import uuid
from returns_demo.isolation import command,environment,service,checker_run
from returns_demo.source import ROOT,baseline_files


def prove():
    canaries=ROOT/'.work'/('returns-probe-'+uuid.uuid4().hex)
    canaries.mkdir(parents=True)
    canary=canaries/'home-secret.txt';canary.write_text('planted-canary-not-a-real-key')
    env_file=canaries/'.env';env_file.write_text('META_API_KEY=planted-only\n')
    # Also attempt to open the repo's actual .env without reading it. A denial,
    # rather than a missing-file error, is required. Never print/read its value.
    repo_env=ROOT/'.env'
    other=socket.socket();other.bind(('127.0.0.1',0));other.listen(2)
    result={}
    probe=Path(__file__).with_name('probe.py').read_bytes()
    try:
        with service(baseline_files()) as candidate:
            for role in ('candidate','checker'):
                packet={'role':role,'canary':str(canary),'env_path':str(repo_env if repo_env.exists() else env_file),
                        'outside_write':str(canaries/'outside.txt'),'other_port':other.getsockname()[1]}
                if role=='checker':
                    # Wait for the real candidate endpoint using only the restricted checker.
                    for attempt in range(30):
                        try:
                            row=checker_run(candidate['port'],{'probe.py':probe},packet);break
                        except ValueError:
                            if candidate['process'].poll() is not None:raise
                            time.sleep(.05)
                    else:raise ValueError('Checker probe could not reach the service')
                else:
                    with tempfile.TemporaryDirectory(prefix='returns-candidate-probe-') as d:
                        root=Path(d).resolve();(root/'probe.py').write_bytes(probe)
                        completed=subprocess.run(command(root,candidate['port'],'candidate','probe.py',candidate['port']),cwd=root,
                            env=environment(root),input=json.dumps(packet),capture_output=True,text=True,timeout=5)
                        if completed.returncode:raise ValueError('Candidate isolation probe failed')
                        row=json.loads(completed.stdout)
                if not row or not all(value is True for value in row.values()):raise ValueError('Isolation condition failed: '+json.dumps(row))
                result[role]=row
        return {'status':'PASS','kind':'actual sandbox denials and restricted checker HTTP','checks':result,
                'candidate_listener':'parent-created inherited IPv4 socket; candidate has no bind or outbound permission',
                'checker_endpoint':'OS permits localhost on selected port; client hard-pins IPv4 127.0.0.1 and never follows redirects'}
    finally:
        other.close()
        for path in canaries.iterdir():path.unlink()
        canaries.rmdir()


if __name__=='__main__':print(json.dumps(prove(),indent=2))
