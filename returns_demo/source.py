"""The baseline is anchored to the already-committed event-built Git blobs."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASELINE_COMMIT='cbe732c'
FILES=('server.py','refund_policy.py','test_existing.py','test_policy.py')

def baseline_files():
 result={name:subprocess.check_output(['git','show',BASELINE_COMMIT+':returns_service/'+name],cwd=ROOT) for name in FILES}
 receipt=json.loads(subprocess.check_output(['git','show',BASELINE_COMMIT+':demo/returns-service/baseline-http.json'],cwd=ROOT))
 if any(hashlib.sha256(data).hexdigest()!=receipt['source_sha256'][name] for name,data in result.items()):raise ValueError('Baseline source receipt mismatch')
 return result
