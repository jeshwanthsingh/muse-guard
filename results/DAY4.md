# Day 4 — approved amendment and local evidence view

## Baseline answer

The original STUDY.md plain mode ended after the initial conflict report. It got
no developer decision or repair opportunity. Comparing recovery with guarded
under that allocation would be circular. The approved dated amendment is
docs/amendments/2026-10-26-day4-fair-recovery.md, shown and approved before commit.
Both modes now receive the same B decision; plain receives only normal chat in
the same Muse session and is independently scored against approved v2 afterward.
Record plain test edits separately; never trust edited tests as scoring evidence.

The fair same-session plain adapter is NOT implemented yet. Both holdout modes
are blocked before paid work; --plain remains initial-only development debugging.
No study or new baseline results are claimed.

## Step evidence

20 root session exports: 4 steps = 3 runs, 5 = 5, 6 = 12. Nine of ten solvables
used six. Shipping stopped at six and reserved the full 160,000 tokens. This is
evidence of inadequate headroom, not proof that a higher limit would pass shipping.
Approved matched limits: 12 steps, 320,000 cumulative tokens, 300 seconds per
initial/repair attempt. Same Standard model, CLI, 2,048 output-token request cap,
exact usage accounting and shared $5 daily ceiling. Reservation $1.36 per attempt;
card reservation remains $0.068. No paid experiments with the new limits today.

## View

`muse-guard view recovery-289db424fb09` opens the real saved refund recovery.
At http://127.0.0.1:8765 it is currently served as a read-only Recorded run.
It shows task/rules, verified witness and advisory explanation, recorded A/B
choice, hash-verified repair diff, 3 visible + 5 hidden passes, final PASS and
original JSON download. No verdict/scoring implementation changed.

`--live` accepts only an existing verified AWAITING DECISION development record
in canonical results/. A real click uses the existing approval, paid runner,
shared lock/cap and independent checker. Replay, invalid tokens/origins and
duplicate decisions are refused. Live continuation was tested with offline
fixtures, not a new paid recovery. The historical replay still costs $0.18794365;
viewing it adds no model spend.

Browser checked at 1280x720: no horizontal overflow, two clashing rules, two
disabled replay choices, eight check rows, zero console errors. Actual download
is byte-identical to results/recovery-289db424fb09.json. Screenshots are in
output/playwright/. Final local suite: 101 tests passed.

## Cost and limits

Day4 model inference spend: $0.00. No real key loaded, no authenticated model
inference, no holdout/study calls. Pre-fix negative tests reached provider auth
with a literal dummy credential and received 401; those tests now have explicit
offline gateway sentinels. The shared calendar-day ledger stays unchanged at
$3.69841705 conservative upper bound, including historical uncertain reservations.

The old $26.80 study estimate assumed only guarded recovery. It is historical,
not a fair-amended-study estimate. The amended campaign permits up to 120
repairs (60 per mode), 60 guarded cards and 240 initial attempts. A conservative
configured token bound is (240 + 120) x $1.36 + 60 x $0.068 = $493.68. This is a
ceiling, not a predicted bill or spend authorization; new matched-run measurements
are required before estimating typical cost.

## Freeze

The original Day3 manifest and 20 holdout pair files remain byte-identical.
The active amended manifest pins this amendment, updated runtime and limits,
including viewer assets, and links to the original manifest hash and commit.
Exact proof is recorded in DAY4_FREEZE_RESULT.json after the local freeze commit.

The full suite also passed from a clean staged snapshot with no .env or
results/raw directory (101 tests), proving the UI tests are portable.

Amended freeze commit: `0f7f736d30d608871e14bf34b50dd3eb090ec122`.
New manifest SHA-256: `18316b3e211dd6f1910ef7770d00a7447a6f0459fd4c0ea18d4cc7aecdbc8633`.
Post-commit verification passed; old data, manifest, scores and ledger unchanged.
