# Corrected holdout study activation — 2026-10-27

User confirmed activation after the supplemental gate passed, authorized a
one-time $70 cap separate from the $5 daily development cap, and prohibited
retries/reruns or patching after an infrastructure failure. Local commits only.

The reviewed corrected draft is retained byte-for-byte in study/. The new
MANIFEST-reviewed-corrected-2026-10-27.json is authoritative for this execution
wrapper. Original active-manifest settings and historical manifests remain
unchanged; the frozen old CLI continues to reject direct holdout execution.
This extension implements the previously disclosed missing study executor.

Scientific allocation remains 20 holdout pairs × 2 twins × 2 repeats × 2 modes
= 160 flows (80/mode; 40 impossible/mode; 40 distinct tasks/mode). No dev reruns.
Stable pair/kind/repeat/mode enumeration is shuffled with preregistered seed
20261026, then saved in HOLDOUT_ALLOCATION-2026-10-27.json before the first call.
Opaque task IDs, task contents, original tests, checker, prompts, same-session
plain decision, guarded card/v2 intervention, B decision and matched limits
(12 steps, 320k tokens, 300 seconds per coding attempt) are unchanged.

The study-specific runner/card files are derived from the frozen implementation.
Reviewed differences: absolute imports, corrected settlement gateway, new
authorization verification, provenance, and the separate ledger. The prompts
and execution/checking logic are unchanged. The orchestrator performs the same
plain/guarded sequence and applies the approved behavior-only external scorer.

Study ledger: study_runs/holdout-2026-10-27, all dates count toward the single
$70 allowance. No midnight reset or hidden draw from the daily budget. Whole-
flow worst-case reservation is $2.788 (two $1.36 phases + $0.068 card),
conservatively required before starting even a solvable flow. Actual usage
settles each phase; all reminders/cards count. Missing usage blocks admission.
Use corrected known-usage settlement with the same phase limits. Client limits
rely on provider metering; an entire provider quota violation is recorded and
stops further calls, never retroactively erased.

No retries, resume or reruns: an existing cohort refuses execution. CLI errors,
export failures, unknown usage, invalid inventories, sandbox faults, source
drift, and non-shutdown gateway blocks stop BEFORE another phase/flow. A normal
agent failure/refusal or candidate-code error is retained as an outcome; the
fixed model-step ceiling is not raised. The model's internal requests/reminders
are counted; no harness phase retry is performed. Never patch while running.

Caffeinate wraps the entire process. progress.log records each flow start/end,
cost and stop; cohort.json checkpoints phase evidence. Raw sessions stay private.
At completion or stop, summary.json retains all assigned denominators, distinct
tasks, primary counts and per-attempt cost/steps including guarded overhead.
An early stop is an incomplete study, not a null result or an estimate from all
assigned flows. Report attempted and assigned denominators separately.

Pre-run estimate from pilot: 758.317 sec / 12 × 160 = 2.81 hours, allow 3–4 hours.
Model cost estimate about $21–$35 for holdouts depending on caching; cap $70.
No accuracy tuning during the study. The requested extractor normalization
change is deferred until successful study completion on a new branch and
requires a NEW evaluation set for any accuracy claim. If infrastructure stops
this study, report first; do not patch the frozen evaluation or silently resume.
