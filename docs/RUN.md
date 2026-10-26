# One-command task recovery

Requires Python 3.11+, Muse Code 1.4.2 and macOS sandbox-exec. No third-party Python
packages. The repository launcher is `./muse-guard`; this Mac also has a reversible
`~/.local/bin/muse-guard` symlink to it.

Load the ignored .env into your shell once; the command reads META_API_KEY only
from the environment. Never commit or print the key.

```sh
set -a
. ./.env
set +a
muse-guard gate --split dev
muse-guard run refund-impossible
muse-guard run refund-impossible --decide B
```

`gate` is offline: it executes Python references, not models. `run` is paid and uses
the shared $5 calendar-day ledger. The default run performs a gated Muse attempt;
after a verified conflict it generates a card, pauses for A/B, creates approved v2,
repairs, rechecks, and prints status/version/checks/cost/record path. Empty input,
EOF or Ctrl-C at the choice leaves AWAITING DECISION with no v2 or repair. `--decide`
records a scripted choice; it does not pretend an interactive human approved it.
`--plain` now runs the amended development flow. It retains an isolated workspace
outside the harness, appends exactly "Rule B wins. Please update the code." with
the same Muse session ID, and never supplies v2 files or verified witness feedback
to that agent. The final checker uses approved-v2 assertions with the candidate's
actual original/runtime rules; it does not gift v2 to a generic interpreter.
Before/after test inventories and original-test tampering are recorded separately.
Both modes require the same final PASS criterion for RECOVERED.

`--remaining-quota` enables the same hard per-request remaining-dollar quota in
both modes. Exact input counts reserve uncached input + worst-case output before
forwarding; terminal usage releases only measured savings. Unknown usage stops
further admission and retains its bound. Normal full-attempt reservations remain
the default. All supported CLI/pilot calls hold canonical results/.run.lock.
No key is printed or sent to the browser.

## Admission and datasets

`datasets/dev/*.json` contains ten pairs. Each pair contains two public rule tables,
a small explicit finite input space, separate visible/hidden input sets, and three
checker-owned reference sources: solvable, v2-A-wins, v2-B-wins. Only approved public
requirements and visible tests are copied into an agent workspace as rules.yaml
(JSON-compatible YAML 1.2) and test_original.py. Hidden inputs/references remain out.

The quality gate enumerates every input (at most 256), proves no solvable overlap
and at least one impossible witness, requires disjoint visible/hidden inputs covering
the complete domain, and executes references against all named checks and the full
domain. Admission binds the actual approved task and exact generated tests, not just
a catalog name. It proves consistency with formal conditions, not the English prose.
The old Day 2 tables are migrated into this catalog; historical result files remain
unchanged. Historical toy fixtures are offline-only and cannot invoke a model.

## Frozen study

The twenty holdout pairs use opaque twin IDs and different domains/wording. They
receive only deterministic/reference validation today. The freeze commit contains
only those data files and MANIFEST.json. The manifest also pins the precommitted
study protocol, dev data and full project runtime, including prompts, labels and
budgets. Its original Git creation commit anchors the manifest; rewriting a working
manifest cannot silently accept drift. Duplicate catalog identities, extra holdout
files, symlinks, source changes and a changed CLI version are refused.

No holdout model run is authorized today. A future authorized study must explicitly
opt in; guarded holdouts require the fixed scripted B-wins decision. Both modes keep
the same initial prompt, checker and permission to report conflicts. Prompts, labels
and budgets must not change after freeze. The original docs/STUDY.md remains the
historical preregistration; study/protocol.json is the operational protocol lock.

## Isolation and cost

Candidates cannot read user homes, .env, common home secrets or other temporary
authoring locations. Network access and outside writes remain denied. Parent-owned
assertions run separately; only approved public rules.yaml is provided as runtime
data. A trusted pre-import handshake distinguishes sandbox readiness from candidate
exit codes. This is bounded macOS confinement, not proof against every OS attack.

The API boundary pins Standard Spark and holds the real key; Muse receives a dummy
key. Input counting and output caps reserve every request, including reminders and
retries, within 320,000 cumulative tokens and twelve main steps per attempt, with a
300-second turn timeout. Maximum reservation is $1.36 per attempt; advisory cards reserve at most $0.068. A pending record precedes
inference. Provider usage is journaled from the first request and reconciled before
session export, including ephemeral reminders. Known cost and retained historical
upper bounds stay distinct. Never delete uncertain spend to reset the cap.

Run `python3 -m unittest discover -q` outside a nested sandbox for offline tests.
All attack/negative-control fixtures are explicitly planted. PASS, TASK FAILURE,
UNAUTHORIZED TEST CHANGE, CONFLICT REPORTED, CONFLICT VERIFIED, CLAIM CONTRADICTED
and HARNESS ERROR remain separate. The shared ledger still carries Day 1 uncertain
reservations because these work stages share calendar date 2026-10-26.

Day3 was pushed with one-time approval; Day4 stays local. No study runs today.

## Local evidence view

```sh
muse-guard view recovery-289db424fb09
# Or serve without opening a browser, on a chosen loopback port:
muse-guard view results/recovery-289db424fb09.json --no-open --port 8765
# Continue an existing verified AWAITING DECISION development record:
muse-guard view <paused-recovery-id> --live
```

Replay is labeled Recorded run and decision buttons are disabled. It reads the saved
verdict, checks and card; it does not rerun a model. Repair diffs require matching
artifact hashes, otherwise the page explicitly says unavailable. Evidence download
returns the original run JSON. Only the chosen record and static assets are served.

Live mode requires environment credentials and an existing verified paused guarded
development recovery. A button records the real choice and uses the existing v2
approval, paid runner, shared budget and independent checker. Page load is free.
Only one decision is accepted. The server binds 127.0.0.1, requires the local Origin
and a per-server token for decision POSTs, and never sends credentials to the browser.
A real live repair was not run on Day4; offline fixtures exercise this continuation.

The approved Day4 protocol amendment and study/MANIFEST-day4.json supersede runtime
hashes and limits from Day3 while retaining its original manifest and holdout bytes.
Both study modes receive a B decision and are scored against the same approved-v2
checker; plain does not see v2 files, verified witness or hidden checks during repair.

## Day5 status and outer authoring boundary

The adapter is implemented and has a real-Muse two-turn test driven by local SSE
fixtures. The final paid corrected pilot is NOT complete: the Day5 attempts found
an isolation-placement bug and a nested Muse sandbox failure before consuming the
remaining daily headroom. See results/DAY5_PILOT.md, including raw outcomes, costs,
uncertainty and exclusions. Do not treat those outcomes as a fair comparison.

Muse authoring now runs inside a single outer macOS Seatbelt policy. Its own
sandbox is disabled only inside that enforced wrapper to avoid unsupported nested
sandbox initialization. The OS policy denies the harness and common home secrets,
restricts writes to the throwaway state, and permits outbound traffic only to the
run's token gateway. Candidate checks keep their existing separate stricter sandbox.
Same-session echo AND actual shell-tool/two-turn integration are tested offline.

The original Day3/Day4 manifests and holdout files remain unchanged. Day5 runtime
changes invalidate their runtime hashes; a new reviewed freeze and a clean dev
pilot are required before any holdout study. Study execution is explicitly blocked.

The polished replay is:
`muse-guard view recovery-289db424fb09-view-day5`.
It adds actual unedited export text, selected decision, approved-rules change and
precomputed behavior observations. For a recovery without display observations,
`python3 scripts/prepare_view.py results/<recovery>.json` creates a separate derived
record using sandboxed observations. The HTTP viewer itself never executes code.
