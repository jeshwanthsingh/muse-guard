# Oct27 correction and separate external-authored evaluation

## Pilot blocker: harness contribution established

The fifth plain shipping repair response reported 6786 input / 2120 output
tokens, although the gateway requested at most 2048 output tokens. The local
request estimate was $0.01736525; actual cost was $0.01749250, a $0.00012725
overrun. The phase had spent only $0.04245365 of its $1.36 allowance.

Replaying the five recorded receipts reproduces the old DollarBudget failure:
“Provider usage exceeded request reservation”. It marks usage unknown and
blocks the next five admissions. The journal's generic labels were misleading:
there was known usage and ample phase/daily budget, not an exhausted daily cap.
The provider exceeded its requested output cap; our harness turned that small
known overrun into a poisoned budget state. This contributed to invalidating
the run. The agent also explicitly refused the repair due to unchanged v1
artifacts; we cannot isolate causality between the blocks and that refusal.

The correction settles known usage against the already-reserved phase allowance,
records estimate overruns, reconciles token totals and retains all limits and
unknown-usage blocking. It lives outside frozen paths. See amendment
2026-10-27-known-usage-settlement.md. The patch was committed as 5a5d40e BEFORE
the one user-authorized corrective flow. No other pilot assignment was rerun.

| Corrective phase | Outcome | Steps | Actual cost | Gateway blocks |
|---|---|---:|---:|---:|
| Initial | CONFLICT VERIFIED | 5 | $0.06802715 | 0 |
| Same-session repair | PASS | 4 | $0.06090415 | 0 |

Total: $0.12893130. Original test edits: none. Original failure retained.
This is a fresh stochastic rerun, so success is not proof the patch alone
changed the agent's decision. The deterministic replay establishes the bug.

The original cohort/gate remains unchanged and failing. The explicitly amended
supplemental gate PASSES, using the existing eligibility checks on the 11 original
flows plus the one hash-linked correction. The corrected descriptive recovery
counts are plain 3/3 and guarded 3/3; original counts remain plain 2/3, guarded 3/3.
No study results are claimed. An uncommitted corrected-freeze draft is prepared
for the user outside the repo in the task's review folder. No active manifest is
replaced. User confirmation and separately enforced one-time $70 study accounting
are still required. No study calls or $70 cap activation today.

## Separate set: Claude-authored, user-reviewed

User approved removal of “no matter what” before any extraction, making doc1's
A/B unconditional with four clashes. Doc2's scoped oversized rule and zero
clashes were confirmed. Source/keys/protocol/scorer were frozen at commit
168e725 before calls. Manifest SHA-256:
`b18f58b6153c7ab5084f74f2df6289aee2e67e1b2c15bd285321c40d6ffd3ab5`.
Original eight-doc corpus, scorer, manifest and results remain unchanged.

| Doc | Correct / truth rules | Wrong | Missing | Matched clashes / truth | Missed | Unmatched (false by rubric) | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| doc1 | 1/4 | 3 | 3 | 0/4 | 4 | 4 | $0.00657750 |
| doc2 | 5/5 | 0 | 0 | 0/0 | 0 | 0 | $0.00572900 |

Doc2 passes (5/5 rules, full coverage without an invented fallback). Doc1 fails
the frozen typed/alias rubric: it used yes/no strings instead of Boolean values,
`over_30_days_old` outside the fixed field aliases, and `stays_active` outside
the fixed action aliases. It nevertheless returned A/B and the four old/top
company witnesses in its own representation. The raw four witnesses are
retained: “0 matched, 4 missed, 4 false” is the fixed matching result, not evidence
that Spark failed to recognize the conceptual clash or invented four unrelated
clashes. Do not expand aliases or normalize new types after seeing results.
The mismatch exposes a representational limitation of this evaluation rubric.
No post-hoc rescue score or repeat call is reported.

Separate set cost: **$0.01230650**. One call per doc, no retries.

## Spend and verification

Previous Oct27 spend $1.64741640 + corrective flow $0.12893130 + this set
$0.01230650 = **$1.78865420**. Remaining daily allowance:
**$3.21134580**. All usage accounted; original failed call costs
remain included. No charges assigned to the future study cap.

Offline validation: 49 scoped correction/spec tests passed, followed by seven
focused final scorer tests. Exact failure replay and live corrected-flow evidence
agree; all 103 protected hashes and original eight-doc manifest verify.
