# One command: spec → decision → implementation → independent recheck

This submission extension is outside the frozen study and the preregistered
8-document extraction evaluator. Neither protected implementation is edited.
The opt-in submission launcher handles `spec`; other commands delegate unchanged.

```sh
cd ~/Projects/muse-guard
PATH="$PWD/submission_tools/bin:$PATH" muse-guard spec demo/continuous/refund.md --fake-response demo/continuous/fake-response.json --accept-all --decide B --out spec_runs/offline-refund
```

One command creates one `run.json` and one `index.html`: exact source quotes,
confirmed/rejected/unconverted items, every conflicting action among confirmed
rules and declared inputs, developer priority, approved v2, implementation diff,
and visible + hidden results for every declared input. The supplied responses are
constructed fixtures, NOT observed Spark/Muse quality. The checker really executes
the candidate in separate sandboxed processes. Existing folders are never overwritten.

Remove `--accept-all` to confirm/reject each proposed translation. Remove `--decide`
to choose priority interactively. For two rules, choose a rule ID such as B. For
larger tables provide a full order such as B,A,C; the highest-priority rule must
participate in a displayed clash. The first matching rule picks ONE next action.
Invalid schemas and uncovered inputs without an approved fallback stop coding.
Rejected rules cannot enter v2. Unconverted sentences remain visible, including
context sentences: the program does not claim it understood their meaning.

The extension reuses the existing source validator, `rules.approve`, `build_task`,
materialization, author sandbox, snapshot freezer and independent checker. It
supplies custom tasks through explicit samples rather than changing the study
catalog. The old recovery entry points remain unchanged. Before final checking,
trusted tests are restored outside the agent folder; agent-side test edits are
reported separately. Behavior against approved requirements decides the result.

Boundaries: 2–256 declared combinations, up to six small fields, supported eq/gte
conditions, one action per input, explicit fallback/priority. The viewer reports
how many inputs actually ran; a harness failure cannot be called complete coverage.
This does not check English extraction fidelity, omitted requirements, undeclared
inputs, hidden real-world state, or arbitrary production software. Repeated runs
of stateful/nondeterministic code are not a proof of all possible executions.

## Tomorrow: one real run, within the shared $5 cap

After the scheduled Day6 pilot has priority and its results are safely recorded:

```sh
cd ~/Projects/muse-guard
git switch codex/submission
python3 submission_tools/check_protected.py
set -a
. ./.env
set +a
PATH="$PWD/submission_tools/bin:$PATH" muse-guard spec demo/continuous/refund.md --real --out spec_runs/real-refund-2026-10-27
```

Review the actual proposed rules, then choose the displayed priority. This invokes
Standard Muse Spark extraction and Muse Code implementation; no model decides
whether a conflicting action is real. The clash card is deterministic in this flow.
Every provider call, including Muse reminders, uses the canonical shared ledger.
Extraction reserves $0.026112; implementation reserves $1.36 (12 steps / 320k tokens /
300 seconds). These are admission bounds, not actual cost. Unknown usage or an
insufficient daily allowance stops execution. Today's date gate forbids paid calls.
Provider transport for the complete flow is not live-tested today.

## New fairness scorer and post-pilot supplement

The developer approved [the behavior-only amendment](amendments/2026-10-26-behavior-only-recovery.md)
on 2026-10-26 before commit. It supersedes recovery scoring and test-edit
interpretation in the historical frozen docs, not their original records.
The exact Day6 runtime remains ef9d36b; the separate scorer uses its trusted
approved-v2 check rows and retains original outcome labels alongside amended ones.
Guarded synchronized v2 artifacts are explicitly part of the intervention.

After the complete pilot, switch back to submission, review its receipts/costs and
then prepare the supplemental freeze (do NOT run this today):

```sh
python3 submission_tools/reviewed_behavior_freeze.py --pilot-root "$PWD" --out results/BEHAVIOR_ONLY_REVIEWED_FREEZE_2026-10-27.json --reviewed
```

It verifies all linked phase hashes using the existing pilot loader, requires a
complete/accounted pilot with valid check inventories, compares recorded runtime
hashes to immutable ef9d36b blobs, and binds the amendment/scorer/parent manifests.
It refuses an uncommitted scorer, incomplete evidence or an existing output.
This supplemental freeze does not rewrite the old active manifest or enable a
holdout executor. A later authorized study must use the frozen external scorer
and the unchanged Day6 agent runtime; otherwise it is not this amended protocol.

## Decision consequence preview — 2026-10-28

The opt-in submission command now shows exhaustive A-wins / B-wins consequences before asking for a decision. It groups witnesses by rule pair and lists every declared input whose action differs under the two choices. Its run viewer and static playground show the same comparison. For more than two rules, the preview explicitly displays both complete priority orders; remaining rules keep their listed order. No choice is inferred from the preview.

```sh
cd ~/Projects/muse-guard
PATH="$PWD/submission_tools/bin:$PATH" muse-guard spec demo/continuous/refund.md --fake-response demo/continuous/fake-response.json --out /tmp/muse-preview-stage
PATH="$PWD/submission_tools/bin:$PATH" muse-guard view recovery-289db424fb09-view-day5 --no-open
```

Choose a new output folder, review each rule and then make the decision. The first command uses labeled fake responses and costs $0. The second displays an existing saved record and makes no model call. Catalog `run <task>` through the same PATH wrapper also prints the preview before its original decision prompt; executing it with real models still requires available budget. The root `./muse-guard` and frozen study entrypoints remain unchanged. New display code lives in submission_tools; no frozen runtime or old evidence is rescored.
