# Day 5 dev pilot — 2026-10-26

This is a partial/flawed development pilot, not a study or fair-comparison result.
No holdout model calls occurred. Raw checker scores are preserved below.

| Task | Mode | Phase | Steps | Actual cost USD | Recorded outcome | Interpretation |
|---|---|---|---:|---:|---|---|
| retry-solvable | guarded | initial | 10 | 0.18780745 | PASS | measured exploratory result |
| retry-solvable | plain | initial | 5 | 0.09907120 | PASS | measured exploratory result |
| retry-impossible | guarded | initial | 4 | 0.08278925 | CONFLICT VERIFIED | measured exploratory result |
| retry-impossible | guarded | card | — | 0.00240325 | GENERATED | measured exploratory result |
| retry-impossible | guarded | repair | 7 | 0.14125460 | PASS | measured exploratory result |
| retry-impossible | plain | initial | 4 | 0.05503820 | CONFLICT VERIFIED | measured exploratory result |
| retry-impossible | plain | repair | 4 | 0.07898875 | PASS | measured exploratory result |
| refund-solvable | guarded | initial | 6 | 0.10957040 | PASS | measured exploratory result |
| refund-solvable | plain | initial | 5 | 0.09471900 | PASS | measured exploratory result |
| refund-impossible | plain | initial | 5 | 0.06753790 | CONFLICT VERIFIED | measured exploratory result |
| refund-impossible | plain | repair | 5 | 0.08143195 | PASS | measured exploratory result |
| refund-impossible | guarded | initial | — | unknown | HARNESS ERROR | interrupted; terminal usage missing for one request |
| shipping-solvable | plain | initial | 2 | 0.04467510 | TASK FAILURE | AUTHORING SANDBOX FAILURE; not a task-quality result |
| shipping-solvable | guarded | initial | 5 | 0.11251090 | TASK FAILURE | AUTHORING SANDBOX FAILURE; not a task-quality result |
| shipping-impossible | guarded | initial | 5 | 0.10737690 | TASK FAILURE | AUTHORING SANDBOX FAILURE; not a task-quality result |
| shipping-impossible | plain | initial | 0 | 0.00000000 | TASK FAILURE | DOLLAR QUOTA STOP; no model inference |

Seven flows finished before isolation review: four solvable PASS and three
impossible recoveries. Plain used the same Muse session and normal follow-up;
no original-test changes were observed. Their retained state was inside the
harness checkout, so hidden-data non-exposure was not established. These rates
must not be compared as a fair experiment.

After moving state outside the checkout, three shipping attempts exposed a nested
sandbox tool-start failure. Their TASK FAILURE rows are infrastructure failures,
not model task failures. The last plain shipping attempt made zero model calls
because the remaining-dollar quota refused its requests. One refund guarded
attempt was interrupted for the isolation fix, leaving one bounded unknown call.

Confirmed Day5 cost: $1.27727245. Day5 total is at most $1.29478145.
One in-flight request is unreceipted; its additional upper bound is $0.01750900.
Shared calendar-day upper bound: $4.99319850 of $5.
No uncertainty was discarded and the ledger was not reset.

## Provisional study cost, not validated for the final adapter

240 initial attempts = 30 pairs x 2 twins x 2 repeats x 2 modes.
Up to 60 plain repairs + 60 guarded repairs + 60 guarded cards.

Observed-cache means: plain initial $0.079091575 (n=4); guarded initial
 $0.1267223667 (n=3); plain repair $0.08021035 (n=2); guarded repair
 $0.1412546 (n=1); card $0.00240325 (n=1).

120 x ($0.079091575 + $0.1267223667) + 60 x ($0.08021035 + $0.1412546 + $0.00240325) = **$38.13**.

Without caching at the same measured token volumes:
120 x ($0.127030125 + $0.1868388333) + 60 x ($0.16744475 + $0.2190015 + $0.00240325) = **$61.00**.

These are cost-only planning projections from completed pre-fix phases. The final
corrected adapter still needs a clean paid pilot with fresh daily headroom before
a realistic study budget or fair outcome comparison is defensible. No study was run.

Final corrected implementation verification: 123 offline tests pass, also from a
clean checkout. This includes actual Muse shell execution and a complete two-turn
same-session repair with planted local SSE responses. It is not new paid evidence.
