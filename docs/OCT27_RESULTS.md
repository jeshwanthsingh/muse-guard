# Oct 27 measured results

Local evidence only. No holdout runs, push or merge. Pilot runtime:
`ef9d36b0e4cf546d45cae469fb61d5d69f27a80e` on day6. Submission spec runtime:
`c284fdaec29c96cb816751d431b96f5721b6ec07`. All paid phases used Standard mode
and the same canonical daily ledger, capped at $5.

## Clean pilot

All 12 assigned flows ran once. All 6 solvable runs passed. All 6 impossible
initial attempts reported verified conflicts. Guarded recovery: 3/3. Plain: 2/3.
No CLAIM CONTRADICTED, original-test edits, or visible-pass/hidden-fail repairs.
These are dev pilot observations, not holdout study results or evidence of
statistical superiority. The original and behavior-only summaries agree here.

| Task | Mode | Phase | Outcome | Steps | Actual cost USD |
|---|---|---|---|---:|---:|
| retry-solvable | guarded | attempt | PASS | 6 | 0.11037970 |
| retry-solvable | plain | attempt | PASS | 5 | 0.09498610 |
| retry-impossible | guarded | attempt | CONFLICT VERIFIED | 4 | 0.07666060 |
| retry-impossible | guarded | conflict_card | GENERATED | — | 0.00255625 |
| retry-impossible | guarded | repair | PASS | 5 | 0.10031415 |
| retry-impossible | plain | attempt | CONFLICT VERIFIED | 4 | 0.07713530 |
| retry-impossible | plain | repair | PASS | 8 | 0.14116540 |
| refund-solvable | guarded | attempt | PASS | 6 | 0.07266825 |
| refund-solvable | plain | attempt | PASS | 6 | 0.07207805 |
| refund-impossible | plain | attempt | CONFLICT VERIFIED | 5 | 0.09645370 |
| refund-impossible | plain | repair | PASS | 4 | 0.08095500 |
| refund-impossible | guarded | attempt | CONFLICT VERIFIED | 5 | 0.05871095 |
| refund-impossible | guarded | conflict_card | GENERATED | — | 0.00234825 |
| refund-impossible | guarded | repair | PASS | 5 | 0.09556685 |
| shipping-solvable | plain | attempt | PASS | 7 | 0.09984940 |
| shipping-solvable | guarded | attempt | PASS | 5 | 0.09609155 |
| shipping-impossible | guarded | attempt | CONFLICT VERIFIED | 5 | 0.06186865 |
| shipping-impossible | guarded | conflict_card | GENERATED | — | 0.00224900 |
| shipping-impossible | guarded | repair | PASS | 4 | 0.08375970 |
| shipping-impossible | plain | attempt | CONFLICT VERIFIED | 4 | 0.07803305 |
| shipping-impossible | plain | repair | TASK FAILURE | 2 | 0.04245365 |

Pilot total: **$1.54628355**; guarded conflict-card overhead is included
($0.00715350). All provider calls, including reminders, have actual usage.
The failed plain shipping repair used 2 steps and explicitly declined to claim
completion because v1 artifacts still conflicted. Policy/budget gateway blocks
also occurred; it did not exhaust today's $5 allowance. No silent retry.
See [freeze review](OCT27_FREEZE_REVIEW.md): the eligibility gate refuses this
pilot, so no reviewed freeze was created or committed.

## Study estimate — not authorization

Full allocation: 30 pairs × 2 twins × 2 repeats × 2 modes = 240 flows.
The pilot has 12 flows including repairs/cards. Scaling factor = 240 / 12 = 20.

- At observed caching: $1.54628355 × 20 = **$30.93**.
- Cached input: 991,517 tokens. Removing the observed discount adds
  991,517 × ($1.25 − $0.15) / 1,000,000 = $1.09066870 to pilot cost.
- Without caching: $2.63695225 × 20 = **$52.74**.
- Holdout-only allocation (160 flows): **$20.62** with the
  observed cache mix, **$35.16** without caching.

This is a three-pair extrapolation, not a quote. The failed short repair may
understate successful-repair cost. A 20% planning margin gives roughly
$37.11 with observed caching or $63.29 without it. Cache hit rates,
domain difficulty and repairs can change. The $5 daily cap still applies; no
study starts before the gate is satisfied and the user approves.

## Real continuous refund run

The user individually confirmed A, B and the fallback, then delegated the
priority decision (“you choose”). The assistant selected B: manual review wins
on the overlapping input. This was an explicitly delegated choice, not an
independent human preference measurement. No --accept-all or --decide flag was
used. The complete record is spec_runs/real-refund-2026-10-27/run.json.

Outcome: **PASS**, 4/4 declared inputs checked (visible + hidden).
Actual cost: **$0.07367885**, including $0.00365700
for extraction. Exact source sentences, v1, decision, v2, implementation diff
and check results are retained together. Friendly tone is unconverted; the
finite checker does not validate prose quality or omitted requirements.

## Original eight-document extraction evaluation

The user clarified that the two human-written docs do not exist yet. Therefore
no corpus amendment was made. The original preregistration/manifest, order,
scorer and aliases stayed unchanged. One real extraction per document; no retries.
Human-written set: **not authored or evaluated**, to be separately preregistered.

Counts include the quoted fallback.

| Document | Correct / truth | Wrong | Missing | Clashes found / truth | Missed | False |
|---|---:|---:|---:|---:|---:|---:|
| refunds | 3/3 | 0 | 0 | 1/1 | 0 | 0 |
| access | 3/3 | 0 | 0 | 1/1 | 0 | 0 |
| shipping | 3/3 | 0 | 0 | 0/0 | 0 | 0 |
| notifications | 2/3 | 1 | 1 | 1/1 | 0 | 0 |
| retention | 3/3 | 0 | 0 | 2/2 | 0 | 0 |
| bookings | 2/3 | 1 | 1 | 0/0 | 0 | 0 |
| pricing | 3/3 | 0 | 0 | 0/0 | 0 | 0 |
| support | 3/3 | 0 | 0 | 0/0 | 0 | 0 |

Six of eight documents passed extraction criteria. Notifications encoded the
fallback as a normal rule; bookings used `reserve_a_seat`, outside the fixed
aliases for `reserve`. Both count as failures under the preregistered rubric;
no post-hoc alias or equivalence adjustment. These failures are structural/label
mismatches, not proof of wrong end-user behavior. All 5 ground-truth clashes
were found, with 0 missed and 0 false clashes. Cost: **$0.02745400**.

## Daily total

Pilot $1.54628355 + continuous $0.07367885 + extraction evaluation
$0.02745400 = **$1.64741640**.
Unknown usage: False. Remaining under $5: **$3.35258360**.
No additional paid runs are needed for this request.
