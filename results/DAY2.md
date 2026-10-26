# Day 2 recovery — 2026-10-26

Stage name Day 2; same calendar day as Day 1. No additional model calls beyond the
one exploratory recovery flow. The study was preregistered in local commit 8bdced2
before this run; no holdout study has been run.

| Phase | Result | Cost USD |
| --- | --- | --- |
| Muse Code v1 attempt | CONFLICT VERIFIED | 0.09834940 |
| Muse Spark conflict card | GENERATED, advisory only | 0.00268375 |
| Simulated developer decision | Rule B wins | 0 |
| Muse Code v2 repair + recheck | PASS: 3 visible, 5 hidden | 0.10829180 |
| **Day 2 total** | **RECOVERED** | **0.20932495** |

Witness: `{"method":"POST","status":429,"idempotent":false}`.
A requires retry; B requires stop. The simulated CLI decision gives B priority
wherever the rules overlap. v1, the witness, decision, approved v2 and both test
hashes are preserved in [the full record](recovery-a61101528cd1.json).
The approved repair returns stop for the witness and passes all extra checker inputs.

## Initial harness error, preserved

The first recheck returned TASK FAILURE because the checker copied solution.py
without the approved public rules.yaml that Muse's general implementation loads.
A regression reproduced this checker omission. Supplying only the trusted approved
table fixed the harness; independently rechecking the **same frozen repair** passed
all eight checks. No requirements/test changes or extra model call were used.
The original checker result and successful offline recheck are both in the record.

No real claim-contradiction or unauthorized-test-change event was observed in this
flow. Those safety behaviors are tested with explicitly planted fixtures.

## Cost and scope

Actual measured tokens across every call, including reminders: input
197148, output 10651, cached input
74888. Total 0.20932495 USD at published
Standard prices, before credits. Initial model flow took 84.631s;
checker-fix offline recheck took 0.503s. Engineering
debugging time is not represented as model-run latency. No missing Day 2 usage.

The shared calendar-day ledger still includes Day 1's conservative reservations;
its upper bound remains below $5. Day 1 scores and records were not rewritten.
Next: seven remaining development pairs, twenty frozen holdouts, then the authorized
paired study; these datasets/study are not claimed complete. See docs/STUDY.md.

Verification: all 66 local tests passed; provider journals account for all 23
Day 2 inference calls, including reminders. Original Day 1 result files and
preregistered STUDY.md were byte-compared unchanged. The shared calendar-day
upper bound is $1.83544020, including historical Day 1 reservations.
