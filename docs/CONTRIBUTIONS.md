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

- Final freeze-only commit: 1e111b8664b88e2a021d0397c15be43d55fdbb83 (20 holdout files plus manifest only).
  Manifest SHA-256: 4e452571fa48c30c11fa4f334b24c94f60db6aef89ec4910b86c06a5ab76a246.
  Freeze verification confirms all protocol hashes unchanged; zero holdout model calls.
  Privacy checks and gitleaks passed after excluding one verified file-checksum false positive.
- Final offline suite: 85 tests passed. Main remains unchanged; day3 remains local.

## Day 4 — 2026-10-26

- Pushed day3 normally at f6f373e using one-time approval, then created day4 from
  that exact head. No main merge or force push; Day4 commits stay local.
- Read the original preregistration before other work: plain stopped after a
  conflict while guarded alone got a decision and repair. Drafted a dated
  fair-recovery amendment, showed it before commit, and received explicit approval.
- Counted main steps from the 20 saved root session exports: 3 used four steps,
  5 used five, and 12 used six. Nine of ten solvables used all six. Approved
  matched ceilings are now 12 steps, 320,000 tokens and 300 seconds per attempt.
- Plain's amended decision is normal chat in the SAME Muse session, without the
  verified witness, v2 agent files or hidden checks during repair. Both modes
  must receive the same B decision and final approved-v2 visible/hidden scoring;
  plain test edits are a separate measure. The same-session adapter is still a
  study blocker; the initial-only --plain path is not a fair recovery baseline.
- Built muse-guard view <run> with recorded replay and explicitly opted-in live
  continuation of a verified paused guarded development recovery. Rendered the
  rules, verified clash/card, A/B choice, hash-bound diff, individual checks and
  JSON download. Kept all checker/verdict logic unchanged.
- Verified the real refund replay in a 1280x720 browser: two highlighted rules,
  disabled replay choices, 8 checks, no horizontal overflow or browser errors.
  The downloaded JSON matches the original byte-for-byte. Saved screenshots.
- Fixed review findings: live mode is restricted to the canonical results ledger
  and lock; diff fixtures no longer depend on ignored raw files; standalone
  attempts resolve public rules only when their saved requirements hash matches.
- Final local offline suite: 101 tests passed. No real key was loaded, no
  authenticated model inference or study run occurred; Day4 model cost $0.00.
  Pre-fix negative tests reached authentication with literal dummy credentials
  and got 401; added explicit offline gateway sentinels to those regressions.
- The amended freeze keeps every original holdout file and the Day3 manifest
  unchanged. New active manifest hash and local freeze commit follow below.
- Clean-checkout verification also passed all 101 tests without .env or ignored
  results/raw artifacts. Staged privacy scan and gitleaks passed.
- Amended freeze commit: 0f7f736d30d608871e14bf34b50dd3eb090ec122.
  New manifest SHA-256: 18316b3e211dd6f1910ef7770d00a7447a6f0459fd4c0ea18d4cc7aecdbc8633.
  Original Day3 manifest SHA-256 remains
  4e452571fa48c30c11fa4f334b24c94f60db6aef89ec4910b86c06a5ab76a246.
  Post-commit verification passed; original data, scores and ledger are unchanged.

## Day 5 — 2026-10-26

- Used one-time permission to push day4 at 9e9bb84 normally; created day5 from it.
  No merge/force push; all Day5 commits remain local.
- Implemented the approved plain adapter. Repeated muse exec with the same session
  ID preserves actual history; original v1 agent files remain unchanged by the
  harness. Only normal B-wins chat is delivered. Independent v2 assertions use the
  candidate's actual runtime rules, avoiding an accidental v2 interpreter gift.
- Added exact before/after test inventories (including empty added/deleted files),
  separate original-test tampering, and a shared PASS recovery criterion. Planted
  paired edits have identical checker/recovery treatment in both modes.
- Started the predeclared retry/refund/shipping dev-only pilot in both modes, with
  12 steps/320k/300s. After the user delegated the cap strategy, added/tested a hard
  remaining-dollar quota rather than resetting the October26 ledger. Actual token
  usage and every known cost remain in per-phase JSON, including reminders.
- Review caught a mistake: retained plain state was inside the harness checkout.
  Stopped the pilot and moved it outside, with OS-enforced harness/secret read
  denials. Early outcomes are explicitly exploratory, not a fair comparison.
- The resumed shipping attempts exposed unsupported nested sandbox initialization.
  Those raw TASK FAILURE rows are labeled infrastructure failures. The last plain
  shipping attempt was quota-blocked and made no inference. Fixed the final code
  with a single enforced outer authoring sandbox, throwaway-only writes and
  gateway-only outbound traffic; the inner Muse sandbox is disabled only inside
  that OS wrapper. Candidate checker confinement remains separate.
- Final integration tests use the real Muse CLI and real shell tools with local
  planted SSE responses, including a full same-session repair and hidden recheck.
  No paid retry was made with the final fix because daily headroom is exhausted.
- Confirmed Day5 cost $1.27727245; upper bound $1.29478145. One interrupted provider
  request lacks a receipt; its remaining bound is $0.01750900. Shared daily upper
  bound $4.99319850, below $5. No uncertainty deleted. No holdout/study calls.
- Cost-only projection from completed pre-fix phases: about $38.13 with observed
  caching, $61.00 with no cache at the same token volumes. Explicit arithmetic and
  sample counts are in results/DAY5_STUDY_COST.json and results/DAY5_PILOT.md.
  A clean final-code pilot remains required before a defensible study budget.
- Polished the display-only viewer: five-step progress, actual trimmed export
  quote, human title, compact conflict card/full-text disclosure, selected B choice,
  v1-to-v2 requirements change and saved witness/nearby behavior observations.
  Code diff is collapsed without blank padding. Fixed template-marker injection.
- Captured overview, decision and behavior screenshots at 1280x720 in an isolated
  headless browser. Discarded one unrelated shared-tab capture before any commit.
  Evidence download matches the derived run record byte-for-byte.
- Original results and both holdout manifests remain unchanged. Day5 runtime drift
  explicitly blocks study use until a new reviewed freeze and clean pilot.
- Final verification: 123 tests passed both locally and from a clean staged
  snapshot without .env or results/raw. Privacy/gitleaks and exact-secret scans
  passed. The full corrected two-turn Muse fixture uses local SSE only.

## Day 6 — 2026-10-26: dated provenance correction

- The initial README no-copy statement ceased to be accurate after Day1 reuse.
  Day1 copied seven Python ast-grep detection patterns into a reference fixture,
  reused detector diagnostic wording and used the source comparison design.
  The initial commit/no-application-code entry and Day1 reuse entry above are
  historical records, not competing claims about today's implementation.
- Deleted docs/tampering-reference.yaml. Replaced the detector with fresh active
  semantic policy records and a new test-scoped AST occurrence implementation.
  Reworded copied diagnostics and rewrote the small legacy identity-inventory
  traversal. New tests catch removed/moved/duplicate predicates, omissions and
  constant checks; unchanged fixtures remain clear.
- Compared the nonignored repository against the local Unfoolable corpus at
  c8eafe7. Beyond the copied fixture/diagnostics, matches were standard Apache
  license/API/HTTP/Git/markup fragments and empty files, not additional identified
  project-specific source copies. Current code uses Unfoolable as a design
  reference only; old commits retain the original material for an honest history.
- Updated README and current PROVENANCE status consistently. The historical
  entries and historical PROVENANCE source table remain intact and labeled.
- Pushed day5 once normally, then created day6. No merge or force push; Day6
  commits stay local. No paid model calls today and no ledger reset.
- Preregistered five primary per-mode measures before the clean pilot/refreeze:
  visible-pass/hidden-fail repairs, explicit claims contradicted, original-test
  edits, recovery rate over all assigned impossible flows, and complete cost/
  steps including guarded overhead. Unknown receipts/steps stay unknown.
- Added a fixed 12-flow dev-only pilot plan for October27 (retry/refund/shipping,
  both twins/modes), date/clean-tree/source-hash/cap guards, reproducible metrics
  and a reviewed-refreeze command that rejects incomplete, budget-blocked or
  infrastructure-failed evidence. Neither pilot nor new freeze ran today.
- Corrected display-only stopped-attempt behavior captions and safely rendered
  inline backtick spans in the actual Muse quote. Verified the recorded refund
  page in an isolated browser at 1280x720; existing run bytes stay unchanged.
- Verification: 147 offline tests passed, including two review regressions for
  budget-blocked freeze evidence and class-level skip decorators. The source
  corpus fingerprint matched before/after. Audit and verification receipts are
  in results/DAY6_PROVENANCE_AUDIT.json and results/DAY6_VERIFICATION.json.
  All prior result files, the ledger and old holdout manifests/data are unchanged.
  Paid calls today: zero; incremental model spend: $0.
- Clean staged snapshot also passed all 147 offline tests without .env/raw
  sessions. All 10 dev pairs passed the exhaustive offline gate. Staged
  gitleaks/private-data scans passed; no Day6 branch was pushed.

### Day6 follow-up — 2026-10-26: child environment confirmation

- Audited Muse version/exec/export and candidate process environment construction.
  Removed the remaining inherited PATH and dummy META_API_KEY environment entry.
  Muse now receives the non-secret gateway credential through documented stdin
  auth; real provider credentials remain only in the trusted parent/gateway.
- Added offline canary tests for arbitrary environment values, both API-key names,
  interpreter options and all three Muse subprocess stages. A sandboxed candidate
  prints its environment and returns it; the test confirms no planted key/value
  reaches that process. No .env file or real key was read for these tests.
- No paid calls or pilot/holdout runs; previous ledgers/results remain unchanged.
- Verification: both environment regression tests and all 149 offline tests
  passed, including real-Muse same-session repair against a local fake provider.
  All 116 prior result/ledger/holdout files checked remain byte-identical.

## Static judge demo — 2026-10-26

- Created codex/static-judge-demo from day6 at ef9d36b. Local commits only.
- Added export-site for a self-contained recorded-run index, run pages and public
  evidence downloads. Reused the viewer presentation; static output contains no
  scripts, live decision controls, runtime server or raw session files.
- Prepared public extracts for historical refund/retry recoveries and a solvable
  PASS. Added an offline checker-scored planted edited-test cheat, prominently
  labeled synthetic and excluded from claims about observed Muse behavior.
- Added allowlisted evidence projection, credential/path/hostname rejection,
  relative links and output hash manifest. Exact current nontrivial .env values
  and the machine hostname were checked against output without printing them.
- Added a manually dispatched GitHub Pages template with a hard-disabled job.
  No repository hosting settings changed, no deployment, push or merge.
- Verified all four pages from file URLs at 1280x720 with zero network requests
  and zero live controls. Fixed Chrome's local-file download behavior using an
  inert data URL; all four actual downloads match the public JSON byte-for-byte.
  Captured index, refund, retry, PASS and planted screenshots.
- No model calls or spend; historical results, the ledger and holdouts preserved.
- Final verification: 155 offline tests passed. Output passed default gitleaks,
  exact nontrivial .env-value, hostname, private-path and email scans. All prior
  116 result/ledger/holdout files checked remain byte-identical. See
  results/STATIC_DEMO_VERIFICATION.json for the artifact/browser proof.


## Spec-to-rules extension — 2026-10-26

- Created codex/spec-to-rules from codex/static-judge-demo at c997d14. Local only.
- Added a separate spec_guard module and opt-in spec_guard/bin/muse-guard wrapper;
  the original launcher, study runtime, prompts, budgets and labels are untouched.
  Existing named-task commands delegate to the original launcher. Confirmed-file
  runs use a separate adapter and never register tasks in the study catalog.
- Built exact-sentence provenance checks, bounded finite-domain validation,
  explicit developer confirmation/rejection, retained unconverted rows and
  exhaustive clash witnesses. Saved source/proposal hashes, quotes and decisions.
  Quote matching is not proof of semantic extraction correctness.
- Added a static spec viewer with highlighted source sentences, review decisions,
  unconverted items, clash cards and an evidence download. Its refund example is
  explicitly a constructed fake Spark response, not observed model behavior.
- Wrote eight natural-English evaluation docs, hand-written rule/default tables,
  explicit expected clashes and fixed action aliases. Preregistered extraction
  and clash measures in docs/SPEC_EVAL.md; a wrong extraction counts as failure.
  The separate manifest fixes inputs/prompt/scoring before tomorrow's real run.
- Added Standard-mode extraction with a shared daily $5 ledger, conservative
  per-call reservation and actual provider usage accounting. Missing usage stops
  further calls; today is blocked before key/network access. Fake-transport tests
  cover exact cost and unresolved reservations. No paid calls or new model spend.
- Verification: 174 offline tests passed, followed by all 21 spec tests after two
  additional review/cost tests. The eight fake evaluation fixtures pass the
  pipeline but provide no model-quality evidence. All 69 protected paths and
  prior results/ledger/holdout/study files remain byte-identical to the base.
- Inspected the viewer at 1280x720: no external requests, no live controls, exact
  downloaded JSON, highlighted quotes and a verified refund clash. Screenshots
  are in output/playwright/spec-*.png. See results/SPEC_VERIFICATION.json.
- Privacy review: demo gitleaks scan clean; four staged generic-key alerts were
  verified file SHA-256 values in manifests/evidence. No private home paths,
  personal emails or local hostname appeared in the staged content.


## Submission preparation — 2026-10-26

- Created local codex/submission at 03b558b, with no push or merge. Rewrote the
  judge README around preflight conflicts, developer decisions and independent
  checks. Study/evaluation outcomes remain explicitly pending.
- Added a submission-only exporter that changes the static index labels, plain
  explanation, four-step strip and GitHub link. Frozen exporter/viewer code is
  untouched. Re-exported output/submission-site; all evidence downloads remain
  byte-identical to the earlier static demo. Captured index/refund at 1280x720.
- Added a hash guard anchored to immutable 03b558b blobs for 103 protected study
  and spec-evaluation files, including working tree, staged content and inventory.
  Installed a branch-specific local pre-commit hook; provided its tracked template.
- Pinned the official experiment runtime to day6 at ef9d36b. Added a standalone
  wrapper that runs the unchanged pilot and creates commit/hash/result envelopes
  for each new/changed result, without changing original hash-linked evidence.
  Future holdout execution still requires pilot review/refreeze and authorization.
- Built an isolated offline-tested Baseten Responses/Chat Completions bridge,
  namespace-tool mapping, streamed response events, terminal usage and cache
  accounting, unknown-usage refusal, and mock-tested HTTPS transport. Pinned the
  hackathon model meta-models/muse-spark-open-1026 from the supplied grant email.
  Kept the one-time credential link out of the repo and did not open it.
- Confirmed planted Baseten/Meta keys, endpoint and arbitrary environment values
  are absent from child and sandboxed candidate environments. Actual Muse Code
  completed a tiny turn against local fake Baseten responses; no provider calls.
- Preregistered the separate 10-dev-pair/two-backend exploratory comparison and
  cost assumptions in docs/BASETEN_EXPLORATION.md. Live execution is BLOCKED pending
  a verified Baseten pre-inference token counter and reviewed balanced executor.
  The live HTTPS transport is implemented but only mock-tested; neither fake
  responses nor public pricing establishes real hackathon billing/compatibility.
- No paid model calls, pilot runs or holdout runs today; incremental spend $0.
- Final verification: all 189 offline tests passed, including 13 submission tests.
  All 103 guarded files and 120 prior result/ledger/study/holdout files are unchanged.
  The static output passed gitleaks and private-data checks; browser loading made
  no external requests and all four cards fit at 1280x720. See
  results/SUBMISSION_VERIFICATION.json. The hook runs the guard before the commit.

## 2026-10-26 — Submission review fixes (offline)

- Developer approved the behavior-only recovery amendment before commit. Both
  modes use the same complete approved-v2 behavioral checks; post-decision test
  edits are descriptive. Guarded synchronized v2 artifacts are explicitly part
  of the intervention. Earlier protocols and scored results remain intact.
- Added an external deterministic scorer and a post-pilot supplemental freeze
  preparer. It requires reviewed, complete, accounted Day6 evidence and binds
  the exact runtime, original manifests and committed scoring policy. No new
  reviewed freeze or holdout execution is claimed today.
- Connected spec review, exhaustive clash search, developer decision, approved
  rules, implementation and independent checks in one submission-only command
  and one page. Reused the existing validation, approval, sandbox and checker.
  The clearly labeled fake refund flow selected B and passed all four declared
  inputs, including hidden checks. A legitimate test edit still passes correct
  behavior; a claimed incorrect fix remains CLAIM CONTRADICTED.
- Bounded current README/demo claims, added source-linked Kiro/ImpossibleBench/
  Harbor related work, retained the Day1-copy/Day6-replacement disclosure, and
  clarified that demo policies return one next action. Frozen historical text
  and original evidence are retained rather than silently rewritten.
- Viewer shows checked/declared inputs, rejected/unconverted content, limits,
  approved priority and a downloadable continuous record. Re-exported the
  static site and inspected new 1280x720 screenshots. No live controls.
- Verified 198 offline tests, all 103 protected hashes, and unchanged prior
  result/ledger/study/holdout evidence. Export privacy and gitleaks scans passed.
  No paid calls; incremental model spend $0. See results/REVIEW_FIX_VERIFICATION.json.
- Tomorrow's separate real spec command and post-pilot freeze procedure are in
  docs/CONTINUOUS.md. The official pilot stays on exact Day6 ef9d36b.

## 2026-10-27 — Real pilot, continuous flow and extraction evaluation

- Ran NEXT_PILOT preflight (149 tests and all 10 dev quality gates) and the
  12-flow clean pilot once on exact day6 ef9d36b. Saved original per-phase results
  and 35 hash-linked provenance envelopes with the exact runtime commit.
- Solvable: 6/6 passed. Impossible: all 6 verified conflicts; guarded recovery
  3/3, plain 2/3. No contradicted claims or original-test edits. The failed plain
  shipping repair honestly declined completion and recorded gateway blocks.
- Freeze eligibility failed on those blocks; the supplemental preparer refused.
  Added a blocked freeze review, not a reviewed manifest. No freeze commit or
  holdout run. Original protocols, outcomes and frozen paths are unchanged.
- Ran the real continuous refund flow on submission after individual user
  confirmation of A, B and fallback. User delegated priority selection; assistant
  chose B. Independent approved-v2 checks passed all four inputs. Saved the
  full run/viewer and separate delegation receipt; no automatic acceptance flags.
- User clarified the two human-written docs have not been authored. Evaluated
  the original eight-doc corpus unchanged, once each. Six extraction successes;
  two rubric failures retained. Found 5/5 clashes, none missed or false. Future
  human-written evaluation remains a separate preregistration.
- Actual spend: pilot $1.54628355, continuous $0.07367885,
  spec evaluation $0.02745400; total
  $1.64741640, all accounted, below the shared $5 cap.
  Per-attempt costs/steps, tables, limitations and study estimate are in
  docs/OCT27_RESULTS.md. No push or merge.

## 2026-10-27 — Separate external-authored spec set (draft only)

- Reconstructed doc1/doc2 at the requested spec_eval/human paths from user-pasted
  text because the files were absent locally. User identifies Claude as document
  author and themselves as reviewer; no human-authorship claim is made.
- Drafted keys and a separate preregistration for review. Flagged the explicit
  top-company exception, oversized-package scope and missing-fallback scorer
  limitation before freezing. Proposed readings have no clashes; the literal
  unconditional job-rule alternative has four and needs user resolution.
- No freeze, paid extraction, answer-key approval or new results claimed.

## 2026-10-27 — Shipping gateway correction, before corrective rerun

- Offline replay proved that a known $0.01749250 provider response exceeded the
  $0.01736525 per-request estimate by $0.00012725. The provider reported 2120
  output tokens against a requested 2048. The old settlement marked known usage
  unresolved and rejected five later requests despite ample phase allowance.
- Added an outside-freeze settlement adapter: reconcile known usage against the
  reserved phase allowance, journal estimate overruns, retain token/dollar caps
  and unknown-usage refusal. Original runtime/results remain unchanged.
- Added exact-receipt replay, HTTP continuation, quota, unknown-usage and token
  overrun regressions. Dated amendment authorizes one fresh plain shipping dev
  flow only, with linked original/corrective evidence and supplemental gate.
- The agent's explicit refusal remains separate evidence; gateway contribution
  does not prove why it refused. No automatic study or $70 allowance enabled.

## 2026-10-27 — Corrective dev result and separate-set freeze

- Authorized single plain shipping rerun on correction commit 5a5d40e recovered:
  5-step conflict report ($0.06802715), 4-step passing repair ($0.06090415),
  $0.12893130 total. No gateway blocks or original-test edits. Supplemental gate
  passes; original cohort and gate remain unchanged/failing, reported alongside
  corrected evidence. No claim that the fix alone caused the improved behavior.
- Applied the user's pre-registration edit removing “no matter what” from doc1.
  User confirmed unconditional A/B, four clashes; doc2 scoped oversized, zero
  clashes; Claude-authored/user-reviewed provenance. Recorded wording rationale.
- Froze the separate set, its approved keys, aliases/whitespace policy, optional-
  fallback scorer, tests and dependencies before any extraction. Original eight
  docs/scorer/manifest unchanged. Future study $70 cap remains unenabled pending
  user confirmation; only the human-reviewed extraction set is next authorized.

## 2026-10-27 — Separate-set results, original scores retained

- Ran each frozen Claude-authored/user-reviewed doc once. Doc2 passes 5/5 rules
  with zero clashes and no fallback. Doc1 fails the fixed representation rubric:
  1/4 correct, 3 wrong/missing, 0/4 matched clashes, 4 missed/unmatched. Raw
  output nevertheless recognizes the four stale/active witnesses using yes/no
  strings and out-of-list names. Reported this distinction, not a semantic
  conflict-detection failure claim; no post-hoc aliases, rescoring or retry.
- Separate set cost $0.01230650; corrective flow $0.12893130; today
  $1.78865420, all accounted below $5. Original eight unchanged.
- Supplemental corrected gate passes; original gate remains failing. Prepared
  an uncommitted draft outside the repo for user review. No study freeze commit,
  holdout calls, push/merge or $70 study-budget activation. Detailed evidence in
  docs/OCT27_CORRECTION_AND_EXTERNAL_EVAL.md.
