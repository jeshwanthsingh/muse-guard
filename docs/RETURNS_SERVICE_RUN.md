# Returns-service run instructions — 2026-10-28

Implemented outside frozen study/evaluation paths on codex/submission. Design: [RETURNS_SERVICE_DEMO.md](RETURNS_SERVICE_DEMO.md). No paid calls were made during the build. The current recorded example uses constructed Spark/Muse replies and a constructed B choice; the HTTP service, sandbox probes and checks actually execute.

## Offline commands

```sh
cd ~/Projects/muse-guard
python3 -m unittest discover -s returns_service -p 'test_*.py' -v
python3 -m returns_demo.preflight
PATH="$PWD/submission_tools/bin:$PATH" muse-guard returns --fake-response demo/returns-service/fake-response.json --out /tmp/muse-returns-fake-example
```

Choose a new output directory. Open the printed index.html. The fake packet is explicitly labeled and supplies the fake review/choice; it does not represent independent human preferences or model performance.

## Tomorrow: exactly ONE real run, with live human review

For **2026-10-29**, after confirming the key is configured in the trusted parent .env and a fresh daily allowance is available:

```sh
cd ~/Projects/muse-guard
python3 submission_tools/check_protected.py
set -a
. ./.env
set +a
PATH="$PWD/submission_tools/bin:$PATH" muse-guard returns --real --out returns_runs/real-2026-10-29
```

Do not add --decide or --accept-all: this command does not implement those flags. Keep the terminal open. It first proves isolation and checks the baseline, then asks the user to confirm/reject each Spark-proposed rule and the fallback. It prints the verified grouped conflict and A/B consequence preview, then pauses for **the user's own A or B input**. “You choose” is not accepted. No Muse Code edit starts before that input. If a translation is wrong, reject it: the run stops and keeps evidence, rather than silently dropping a requirement or making another extraction call.

Standard model muse-spark-1.3 is pinned. Extraction has a 6,144-total-token ceiling; service editing has 12 model steps / 320,000 total tokens / 300 seconds. Every provider request, including reminders, is journaled through the gateway from its first request, then reconciled to actual usage. Both phases use the existing shared daily $5 ledger, not the study allowance. Conservative maximum phase reservations are $0.026112 + $1.36 = $1.386112; this is a reservation, not a measured price or guaranteed provider quote. Unknown usage stops further calls. No automatic retries. An existing output folder is refused.

The real date gate rejects paid execution before or after Oct 29 under this one-run preparation. Root session export and full stdout/stderr are retained privately under the run's raw/ directory; provider receipts are in the daily ledger and copied into the structured service record. A failed phase still contributes its receipt to the record. Raw session data must not be published.

## Evidence and scope

Each run retains baseline source hashes and actual HTTP traffic, isolated-channel proof, the quoted extraction/review, grouped witness/preview, v1, explicit decision, approved v2, approved visible-test change, source snapshots/diff, actual before/after responses, test IDs/layers/results and actual cost. The baseline comes from immutable event-built commit cbe732c. Existing HTTP regressions are restored from that commit in a checker folder outside the agent folder; original-test edits are descriptive. The reference interpreter generates expectations only, not candidate implementation.

**Policy behavior checked over these declared cases.** Four Boolean eligible/fraud_hold combinations are checked by create → evaluate → get HTTP operations. Three policy cases have visible tests; the fourth is checker-only. Seven service regressions check the existing endpoint/storage/validation behavior. Each phase starts a fresh in-memory service with the same synthetic inputs; there is no claim of persistence across restarts or exhaustive API verification.

The candidate inherits a parent-bound IPv4 loopback socket: no new binds or outbound connections. The checker OS profile allows localhost at that selected port; its client pins IPv4 127.0.0.1, takes only endpoint-relative paths and does not follow redirects. Both children deny home/secret reads and outside writes, and receive an allowlisted environment without any provider key or arbitrary .env values. This remains a macOS demo, not a production service or a general security boundary for hostile native code.
