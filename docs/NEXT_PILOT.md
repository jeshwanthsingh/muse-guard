# Clean pilot and reviewed freeze — planned for 2026-10-27

Prepared 2026-10-26 in America/Los_Angeles. Do not execute the paid command today.
No automation is scheduled. The executable date guard refuses any other date.
Use the final committed Day6 code; do not rerun scripts/day5_pilot.py or reset/delete
old cost records. The fresh $5 allowance is a new calendar date in the same ledger.

The immutable plan is study/clean_pilot_plan.json: retry, refund and shipping,
solvable + impossible, one repeat, both modes = 12 flows. Modes use the recorded
seed/order, same B decision and same 12 steps / 320k cumulative tokens / 300 seconds.
All phase costs/reminders/cards count against the shared $5 ceiling. A budget stop
is retained, never replaced by a successful retry. No holdout model calls.

Run these commands manually on October27 (the clean tree/date gates are enforced):

```sh
cd ~/Projects/muse-guard
git switch day6
git status --short
python3 -m unittest discover -s tests -q
./muse-guard gate --split dev
python3 scripts/clean_pilot.py --plan
set -a
. ./.env
set +a
python3 scripts/clean_pilot.py --execute
python3 scripts/clean_pilot.py --summary results/CLEAN_PILOT_2026-10-27.json
```

The execute command refuses an existing output, a dirty source tree, a date other
than October27, an invalid dev allocation, insufficient/unknown spend, or source
changes during the pilot. It writes results/CLEAN_PILOT_2026-10-27.json and pins
both source and per-phase record hashes. No automatic repeat or overwrite.
The summary implements the preregistered PRIMARY results, with all assigned
impossible flows in each mode's recovery denominator.

**Stop and review:** inspect all primary counts, per-attempt usage/steps, claims,
original-test edits, visible/hidden inventories and any failure or missing receipt.
A clean pilot may have genuine task failures; infrastructure errors, missing usage,
no-inference stops and changed source cannot support a reviewed freeze. Fixing
runtime after this pilot requires another explicitly planned pilot, not relabeling
these results as evidence for new code. Do not run a holdout study.

After review is complete, create the new manifest and commit it locally:

```sh
python3 scripts/reviewed_freeze.py --pilot results/CLEAN_PILOT_2026-10-27.json --reviewed
git add study/MANIFEST-clean-2026-10-27.json
git commit -m "Freeze reviewed code after clean development pilot"
python3 -c 'from muse_guard.freeze import verify_freeze; print(verify_freeze())'
```

The new manifest includes the primary-measure plan, detector policy, all runtime and
pilot scripts, unchanged holdout hashes, reference validation, the pilot hash and
both retained parent manifests. It becomes verifiable only after its creation
commit exists. --reviewed records a local review declaration; it does not prove an
external human identity. No merge, push or holdout execution is authorized here.
Keep tomorrow's new evidence in local commits separately after inspecting git status.
