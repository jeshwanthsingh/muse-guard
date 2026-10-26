# Day 3 development results — 2026-10-26

All values below are development/debugging evidence, not registered study results.
No model has run on a holdout task.

## Task gate

10 dev pairs and 20 holdout pairs passed exhaustive finite-domain admission.
All 90 references passed (one solvable + both possible v2 winners per pair).
Visible and hidden cases are disjoint and together cover every finite input.
Planted broken solvable twins, impossible twins without a witness, missing/bad
references, unsampled conflicts and changed task wrappers are refused.
The gate proves formal table consistency; it does not independently interpret English.

## Dev models

| Pair | Solvable | Impossible | Initial cost USD |
| --- | --- | --- | --- |
| access | PASS | CONFLICT VERIFIED | 0.21095055 |
| discount | PASS | CONFLICT VERIFIED | 0.17456310 |
| feature | PASS | CONFLICT VERIFIED | 0.14636710 |
| notification | PASS | CONFLICT VERIFIED | 0.16894195 |
| pricing | PASS | CONFLICT VERIFIED | 0.15771755 |
| rate-limit | PASS | CONFLICT VERIFIED | 0.16231755 |
| refund | PASS | CONFLICT VERIFIED | 0.16014175 |
| retention | PASS | CONFLICT VERIFIED | 0.14604915 |
| retry | PASS | CONFLICT VERIFIED | 0.15554380 |
| shipping | TASK FAILURE | CONFLICT VERIFIED | 0.19244070 |

20 initial attempts: {'CONFLICT VERIFIED': 10, 'PASS': 9, 'TASK FAILURE': 1}.
Shipping-solvable stopped at six main-model steps, with the starter unimplemented
and no completion claim. It remains TASK FAILURE; no successful score was substituted.
Initial dev model cost: **$1.67503320**. Offline gate/reference execution: $0.

## One command

`muse-guard run refund-impossible --decide B` completed the full flow:
verified conflict, real advisory card, scripted B-wins receipt, approved v2,
Muse repair, independent PASS on 8/8 checks. Cost **$0.18794365**.
The no-flag path asks interactively; invalid/empty/EOF choices are covered by tests.
Full record: [recovery-289db424fb09.json](recovery-289db424fb09.json).

**Day 3 actual measured total: $1.86297685.**
All provider usage is recorded, including reminders. The shared calendar-day upper
bound, including prior-day-stage uncertain reservations, is $3.69841705, below $5.

## Study estimate, not a study run

30 pairs x 2 twins x 2 repeats x 2 modes = 240 initial attempts.
30 impossible twins x 2 guarded repeats = at most 60 card/repair recoveries.
Measured mean initial cost: $0.08375166; card $0.00245450; repair $0.10925640.
**240 x $0.08375166 + 60 x ($0.00245450 + $0.10925640) = $26.80.**
No-cache sensitivity at the same token volumes: $45.82. These are planning
estimates from 20 dev attempts and one recovery, not guarantees or fresh authorization.
Hard token-ceiling bound: 240 x $0.68 + 60 x ($0.068 + $0.68) = $208.08.
The campaign is not run today; each future calendar day still has a $5 cap.

## Freeze

The separate freeze-only commit and manifest SHA are recorded in FREEZE_RESULT.json.
All prompts, labels, budgets and runtime/dev hashes are pinned before holdout model use.
No page/web UI was built; that is a later display-only task.

Freeze commit: `1e111b8664b88e2a021d0397c15be43d55fdbb83`.
Manifest SHA-256: `4e452571fa48c30c11fa4f334b24c94f60db6aef89ec4910b86c06a5ab76a246`.
The commit contains only the 20 holdout pairs and manifest. Post-commit integrity
verification passed with protocol UNCHANGED and zero holdout model calls.
Gitleaks found one file-checksum false positive; its exact computed SHA-256 was
verified and excluded, with the remaining scan clear.

Final offline verification: 85 tests passed, including planted bad pairs,
freeze drift controls, interactive decision handling, budget and sandbox regressions.
