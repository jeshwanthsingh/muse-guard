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
`--plain` performs only the initial attempt with the same checker/report permission.

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
retries, within 160,000 tokens and six main steps per run. Maximum reservation is
$0.68 per attempt; advisory cards reserve at most $0.068. A pending record precedes
inference. Provider usage is journaled from the first request and reconciled before
session export, including ephemeral reminders. Known cost and retained historical
upper bounds stay distinct. Never delete uncertain spend to reset the cap.

Run `python3 -m unittest discover -q` outside a nested sandbox for offline tests.
All attack/negative-control fixtures are explicitly planted. PASS, TASK FAILURE,
UNAUTHORIZED TEST CHANGE, CONFLICT REPORTED, CONFLICT VERIFIED, CLAIM CONTRADICTED
and HARNESS ERROR remain separate. The shared ledger still carries Day 1 uncertain
reservations because these work stages share calendar date 2026-10-26.

Day3 commits stay local. The one-page run web view is future work, not built today.
