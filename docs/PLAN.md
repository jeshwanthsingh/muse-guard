# Day 3: task admission, one command, and holdout freeze

Work stage Day 3, calendar 2026-10-26. day2 was pushed once with permission;
all day3 commits remain local. Existing calendar-day spend/reservations remain counted.

1. Build an exhaustive finite-domain quality gate first. Reject solvable overlap,
   impossible no-witness, duplicate visible/hidden inputs, bad/missing references,
   and oversized domains. Execute every solvable and both winner-v2 references
   against visible/hidden checks plus the complete domain, without model calls.
2. Migrate three existing development pairs to explicit finite schemas; author
   seven more varied pairs. Admission is mandatory before any model run.
3. Add `muse-guard run TASK`: same initial prompt and checker, advisory card after
   verified conflict, then an interactive developer choice or explicit --decide.
   No decision means no approved v2 and no repair. Print evidence and save record.
4. Debug only on dev tasks within the shared $5 cap. Keep actual model usage and
   reference/gate checks separate. Settle prompts, labels and budgets before freeze.
5. Author 20 holdout pairs in different domains and wording, with opaque twin IDs.
   Run only deterministic/reference validation. Freeze the 20 files alone with a
   SHA-256 manifest that also pins precommitted study protocol/runtime hashes.
6. After freeze, refuse protocol/prompt/label/budget drift. No holdout model calls
   today. Add no UI; the one-page run view is a later task.

Verification: planted broken pairs rejected; all 30 pairs gated; all references
pass; interactive and scripted decision paths; ledger/usage; gitleaks/privacy;
freeze-only commit contents and manifest/runtime hash verification.
