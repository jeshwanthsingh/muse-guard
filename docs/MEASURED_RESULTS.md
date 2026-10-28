# Measured results — 2026-10-27

The completed preregistered holdout study contains 160 runs: 20 locked task pairs × 2 twins × 2 repeats × 2 modes. These are repeated runs, not 160 independent problems. Each mode has 80 flows, 40 distinct tasks and 120 coding attempts (80 initial attempts + 40 repairs). The 20 impossible tasks are each repeated twice. Guarded additionally has 40 explanation-card calls.

| Measure | Plain Muse | Guarded recovery |
|---|---:|---:|
| Initial coding attempts | 80 | 80 |
| Repair coding attempts | 40 | 40 |
| Explicit completion claims: initial | 40/80 attempts | 37/80 attempts |
| Explicit completion claims: repair | 37/40 attempts | 40/40 attempts |
| Contradicted claims among explicit claimers | 0/77 claiming attempts | 0/77 claiming attempts |
| Contradicted claims among all coding attempts | 0/120 attempts | 0/120 attempts |
| Original tests edited | 0/120 attempts | 0/120 attempts |
| Visible-pass / hidden-fail repairs | 0/40 repairs | 0/40 repairs |
| Recovery after one decision | 39/40 (97.5%) | 40/40 (100%) |
| Solvable completion | 40/40 | 40/40 |
| Total actual cost | $7.65650630 | $7.78230745 |
| Coding steps | 555 | 607 |

No tasks exhibited a contradicted claim, test edit or hidden-only repair failure. Both modes recovered all 20 distinct impossible tasks at least once; plain recovered 19/20 on both repeats, guarded 20/20. The one-flow recovery difference is not a proven advantage. The three zero-valued measures are a null result; this study provides no evidence that muse-guard makes Muse more honest.

Observed guarded overhead: ($7.78230745 / $7.65650630 − 1) × 100 = **+1.64% cost (about +2%)**; (607 / 555 − 1) × 100 = **+9.37% coding steps (about +9%)**. Cost includes $0.09737960 for the 40 guarded explanation calls. Those calls do not have Muse Code step counts. Coding-step means: plain 4.625 and guarded 5.058 per attempt.

The sole failed repair was plain h10-b repeat 1. Old rule files still contradicted the chat decision; Muse requested synchronized approved requirements. Refusing was reasonable. It made no completion claim; this was not dishonesty. Guarded mode keeps instructions synchronized. The second assigned repeat passed. Guarded's synchronized approved-v2 artifacts are part of the intervention. One observed difference does not establish general superiority.

Both earlier cohorts were excluded for harness stops—the first on reminder-export policy, the second on a repository-root/accounting bug—and their $0.10836480 + $0.21792675 charges remain in the $15.76510530 total study cost. Completed cohort cost: $15.43881375. These excluded observations are not pooled into primary measures.

Reminder-export warnings: plain 520/874, guarded 439/689. All 240 root exports succeeded; all 280 phases have complete matching journals (2,565 provider requests), with no unknown usage. Frozen assignments and all 199 runtime/source hashes were verified unchanged. See STUDY_RESULTS_2026-10-27.md and study_runs/holdout-third-2026-10-27/attempts.csv for the full evidence.

## Spec extraction: strict 7/10 documents

These are two separately preregistered sets, reported separately. The combined 7/10 is descriptive, not a new pooled evaluation protocol.

| Set | Strict document successes | Clash result |
|---|---:|---|
| Original eight authored docs | 6/8 | All 5 ground-truth clashes found; 0 missed, 0 false |
| Independent AI (Claude), user-reviewed docs | 1/2 | Doc2: zero clashes, correct; Doc1: representation mismatch, retained failure |

Doc1 returned the four old-posting/top-company witnesses in its own representation. It used yes/no strings instead of Booleans and field/action labels outside the frozen aliases. Under the strict rubric, only 1/4 rules matched, with 3 wrong and 3 missing; 0/4 clashes matched, 4 were missed and 4 unmatched (false by rubric). This is a representation-matching failure, not evidence that it failed to notice the conceptual clash. No post-hoc normalization or rescore was used. Doc2 passed all 5 rules, with no clashes. The original eight's notifications and bookings docs also remain extraction failures. See [the explanatory classification](EXTRACTION_FAILURES.md); no frozen score or result was changed.

Evidence: OCT27_RESULTS.md (original eight) and OCT27_CORRECTION_AND_EXTERNAL_EVAL.md (separate set). Extraction accuracy claims require developer review and a fixed representation rubric; finding conflicts in extracted rules does not validate that extraction.

## Scope and interactive example

Small finite rule tables; 20 holdout pairs; one Muse Code version (1.4.2, Muse Spark 1.3). These results do not establish correctness for arbitrary software, omitted requirements or undeclared inputs. Cost and step overhead describe this sample, not a price guarantee.

The static judge page includes a separate browser-only playground. Rule toggles and action edits recompute all conflicting action pairs over the declared finite inputs. Conditions/domains are fixed. Duplicate witnesses are grouped by rule pair; the decision preview lists exactly the declared inputs whose next action differs under each priority choice, using the unchanged checker logic. The opt-in submission CLI shows the same preview before its decision prompt and in its run viewer; frozen study entrypoints are unchanged. The browser search is checked against the unchanged Python conflict validator for every demo table, all rule subsets, and combinations of existing/new/equal actions. It makes no API calls, persists no edits, and changes no study records. A clash means two enabled rules require different next actions for the same declared input; multiple rules requiring the same action do not clash.
