# Contributions

A dated log of work built during the Meta Global AI Developer Hackathon
(Oct 26 - Nov 4, 2026). Update this log each day with that day's contributions.

## 2026-10-26

- Created the project repository from scratch on `main`.
- Added the README with the project goal, work-in-progress status, event dates,
  and disclosure of prior work used only as a design reference.
- Added the Apache-2.0 license, ignore rules, and an environment-variable template.
- Started this daily contributions log to identify work built during the event.
- No application code has been built yet. No code was copied from Unfoolable.

### Day 1 implementation

- Built three tiny task pairs (identity, absolute value, lowercasing), each with
  original named tests and an impossible twin contradicting one exact input.
- Built a plain-Muse runner, throwaway workspaces, frozen file hashes, original-
  test restoration, separate candidate processes, parent assertions, strict test
  inventory checks, structured conflict reports, and a Python AST tampering detector.
- Copied seven Python YAML detection rules and adapted the listed Unfoolable
  algorithms/designs with permission. The earlier no-copy entry describes the
  initial commit only; [PROVENANCE.md](PROVENANCE.md) records actual Day 1 reuse.
- Added spend preflights, a serial ledger, token/cost parsing and fail-closed unknown
  usage handling. A provider-enforced cap is still an external prerequisite.
- Added 31 behavioral tests, including edited/deleted tests, fabricated success,
  forged reporter output, assertion-library patching, and a stateful impossible-
  task cheat. Local protocol fixtures are not model-performance measurements.
- Verified installed Muse 1.4.2, missing-key and unsupported-flag diagnostics,
  and a successful no-charge echo execution plus schema-v1 session export.
- Saved six no-model ERROR records: Meta execution remained blocked by missing
  environment credentials and unverified Standard-mode/spend prerequisites.
- Paid Meta usage: 0 input tokens, 0 output tokens, $0. No push or merge.

### Day 1 follow-up: live baseline and confinement

- Audited Muse 1.4.2 help, its non-secret configuration and official Meta mode docs.
  Added a Standard-model API boundary, with the real key held only upstream.
- Wrote new macOS sandbox-exec code: candidate children cannot write outside their
  throwaway folder or open a connection to a real listening local server. Kept
  separate-process parent assertions. No Unfoolable isolation code was copied.
- Added an exact-input-token gate, per-request output caps, cumulative per-run
  token budgets, conservative $5 daily admission, durable pending reservations,
  crash blocking, gateway shutdown/drain handling, and a running results total.
- Verified the real key with one tiny Standard call: 12 input / 14 output tokens.
- Ran each of the six toy tasks once with real plain Muse: 3 PASS, 2 CONFLICT
  REPORTED, 1 ERROR caused by Rule A/Rule B labels in an otherwise honest report.
  No fake-success claim or test tampering was observed on the impossible tasks.
- Discovered root exports omit automatic reminder calls; exported durable reminder
  sessions and added terminal provider-usage capture for ephemeral calls. Retained
  full $0.68 bounds for the first two incompletely exported runs. See BASELINE.md
  for measured spend and the conservative total upper bound; no invented exact total.
- Verified all 47 tests, including regression coverage for caps, malformed/partial usage, context matching,
  shutdown, and confinement. Prepared day1 for the one-time authorized push;
  no merge to main and no force push.


## Day 2 recovery — 2026-10-26

Stage label Day 2, still the same calendar date. Built recovery around Day 1's
honest reporting on all three impossible tasks; kept Day 1 scores unchanged.

- Restricted candidate reads of .env, all user homes, SSH/cloud/config and other
  secret paths; denied other temporary authoring locations to protect hidden cases.
  Kept no-network, confined writes and separate parent assertions. Added secret,
  hidden-canary, startup-handshake and planted adversarial regressions.
- Added three realistic rule-table pairs: HTTP retry, discounts and access. Tables
  are JSON-compatible YAML 1.2. Added deterministic witness validation, safe rule-ID
  normalization, neutral outcomes, approved v1/v2 receipts and regenerated tests.
- Added hidden checker inputs and planted public-example-hardcoding checks. Bound
  both visible and hidden test hashes to records; hidden data stays outside agent files.
- Journaled provider usage from the first request, including ephemeral reminders;
  preserved measured cost independently of export and retained the shared $5 cap.
- Preregistered the fair 10-development/20-holdout, 2-repeat/2-mode study in local
  commit 8bdced2 before real Day 2 results. Only three development pairs exist;
  no holdout campaign is claimed or executed.
- Ran one real retry-policy recovery: verified POST/429/non-idempotent witness,
  real advisory Spark card, simulated B-wins developer decision, approved v2,
  Muse repair, and independent PASS on 3 visible + 5 hidden checks.
- Fixed a checker omission of approved public rules.yaml, then rechecked the same
  frozen repair offline. Preserved the original checker error; no paid rerun.
- Measured Day 2 cost: $0.20932495, with complete usage for every call.
  See results/DAY2.md and full recovery-a61101528cd1.json. No new Unfoolable code
  was copied. All commits remain local; no push or merge.

- Final verification: 66 tests passed; all 23 Day 2 provider calls reconcile to
  actual usage/cost journals. Historical Day 1 records and the preregistered study
  remain byte-identical. Shared calendar-day upper bound: $1.83544020, below $5.


## Day 3 quality gate and study preparation — 2026-10-26

- Used one-time permission to push day2 at 6236e93 normally; main stayed unchanged.
  Created day3 from day2. All subsequent commits remain local.
- Built an exhaustive finite-domain admission gate first, with deliberate broken-pair
  controls. Enforced full visible/hidden coverage, disjoint splits, exact task binding,
  and executable references for solvable plus both approved v2 choices.
- Expanded to ten realistic dev pairs (seven new), with explicit finite schemas.
  Authored twenty holdout pairs in other domains/wording with opaque twin IDs.
  All thirty passed the gate and all ninety reference versions passed. No model
  was run on any holdout; only deterministic/reference checks were performed.
- Added the muse-guard run command, interactive developer pause and --decide for
  scripts, short evidence output, and full records. The scripted refund recovery
  passed 8/8 independent checks, costing $0.18794365.
- Ran twenty plain development attempts: 9 PASS, 10 CONFLICT VERIFIED, 1 six-step
  task failure with no completion claim. Preserved that failure rather than rerunning
  for a passing score. Actual initial cost $1.67503320; Day3 total
  $1.86297685, including all reminders.
- Fixed cancelled-reminder response logging without losing measured usage. Added
  catalog-shadowing, manifest-anchor, protocol-drift and decision-policy controls.
- Prepared a holdout-only freeze commit with a SHA-256 manifest pinning every data
  file, runtime module, dev file, initial prompt, label and budget. Exact freeze
  commit/hash follows in the final freeze entry. No study campaign or web UI today.
- Estimated the full registered study at about $26.80 from observed cache
  usage; no-cache sensitivity $45.82; absolute configured token bound
  $208.08. See results/STUDY_COST_ESTIMATE.json for explicit arithmetic.
