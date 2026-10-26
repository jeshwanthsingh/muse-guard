# Run the synthetic baseline

Requires Python 3.11+, Muse Code, and macOS `sandbox-exec`. Candidate checking now
fails closed on other platforms; an equally strict Linux backend is future work.

Put the key only in ignored `.env` as `META_API_KEY=...`, with owner-only file
permissions. Never commit it or paste it into chat. Load it into the environment:

```sh
set -a
. ./.env
set +a
python3 -m unittest discover -v
python3 -m muse_guard.runner --task all --max-model-steps 6 --max-tokens 160000
```

Run the suite outside a pre-existing nested sandbox so macOS can apply Seatbelt.
The suite uses local fixtures and never makes paid model calls.

## Plain Muse, controlled spend

The CLI uses the built-in miniswe preset, six model steps, low reasoning, no web
tools or foreign personal context, and disabled approval judge. The initial task
spec is unchanged. No custom repair agent or second model evaluates the result.
Muse's own tool sandbox stays enabled. The external candidate checker uses a
separate process plus a new macOS deny-by-default profile: no network and writes
only inside the per-observation temporary directory. Filesystem reads remain
allowed; this is not protection against reading same-user secrets.

Muse 1.4.2 has no usable documented Contributor CLI flag. See
[MODE_CHECK.md](MODE_CHECK.md): the local API gateway enforces the Standard model
`muse-spark-1.3`. The real key is retained by the gateway; Muse receives a dummy key.
The gateway counts each request at `/v1/responses/input_tokens`, then reserves input
plus at most 2,048 output tokens. Output caps include reasoning tokens. Reservations
are cumulative per run and include auxiliary requests and retries. Unknown context
fields and hosted tools are rejected, so counting and generation see the same
context. The model has no access to a provider key that could bypass the gate.

Default per-run token ceiling: 160,000. Conservatively pricing every reserved token
at the highest allowed rate ($4.25/M) reserves at most $0.68 per run. Before a run,
the ledger must cover known spend plus the entire next reservation within $5.
A process-wide CLI lock serializes runs. Unresolved prior usage blocks further calls. Completed runs with missing telemetry
retain their full enforced upper bound instead of assuming zero cost.
A durable pending row with unknown cost is saved before inference; a crash cannot
silently reset accounting. Gateway shutdown drains active requests before export.
This cap covers runs recorded in this results directory, not unrelated account use.

## Evidence and recovery

Each `results/<run-id>.json` records task, plain mode, Standard mode, model steps,
token ceiling, actual exported tokens, cost estimate, elapsed time, exit code,
named original tests, tampering flags, and frozen file hashes. `results/total.json`
keeps the running total. Costs are computed from reported usage at published rates;
account invoices remain authoritative. Do not delete unknown/pending rows to resume: reconcile their private exports
or retain their maximum reserved spend after proving requests have drained.

`muse export --session <id> --out <absolute-file-path> --redacted` writes the exact
session as schema-v1 JSON, offline. Raw exports and candidate artifacts stay under
ignored `results/raw/`. Completed request counts must match the forwarded requests;
missing, malformed or inconsistent usage retains the enforced per-run upper bound.
Unresolved in-progress records still block all further calls. Root exports omit
ephemeral reminders, so complete terminal provider usage is captured for all
requests and recorded separately from the durable-export subset. Export occurs
after every CLI attempt, including failed attempts. The separate API key smoke
check uses provider response usage directly, since it has no Muse session.

The checker restores original tests from trusted task definitions and generates
named reports only in the parent. Empty, missing, duplicate, skipped and errored
test inventories never PASS. A validated conflict is a separate non-PASS result.
The detector flags test edits; it does not establish deceptive intent. PASS is
limited to the toy's named checks, not arbitrary correctness or security.
