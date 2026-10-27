# Holdout restart plan — October 27, 2026

**Not authorized to run yet.** Local only. Preserve the stopped cohort and the original runtime/freeze. User clarified that the restart is 160 holdout flows only, not 240. Copy the exact ordered rows from study/HOLDOUT_ALLOCATION-2026-10-27.json. No reshuffle, new assignments or added dev flows. New cohort: holdout-restart-2026-10-27. The previous h13-b attempt is reported separately as **excluded: harness stop**, not pooled into model outcome measures.

The original one-time cap is $70. Its prior $0.1083648 remains charged: $70 - $0.1083648 = **$69.8916352 available for restart**. The restart ledger reads original and new phase receipts across all dates, without counting wrapper totals. The two development smoke flows use the shared $5 daily ledger instead. No unknown-cost admission. Every flow conservatively requires $2.788 remaining; per-phase gateway quotas and token/step/time limits remain unchanged. No phase/flow retry or resume; infrastructure failure stops.

The preparation command creates a DRAFT only and verifies two completed smoke flows, their source hashes, receipts and old freeze. The draft binds new runtime and smoke evidence alongside old protected dependencies. Review this draft before activation. No approved restart manifest exists yet, so execution is blocked.

Commands prepared now (offline):

```sh
cd ~/Projects/muse-guard
python3 -m submission_tools.restart_study --prepare
python3 submission_tools/check_protected.py
```

**Only after explicit approval**, activate and commit the reviewed freeze, then execute once:

```sh
cd ~/Projects/muse-guard
python3 -m submission_tools.restart_study --activate
python3 submission_tools/check_protected.py
git add study/MANIFEST-restart-approved-2026-10-27.json
git commit -m "Activate reviewed reminder-export restart freeze"
python3 -m submission_tools.restart_study --verify
set -a
. ./.env
set +a
mkdir -p study_runs/holdout-restart-2026-10-27
caffeinate -dimsu python3 -u -m submission_tools.restart_study --execute > study_runs/holdout-restart-2026-10-27/console.log 2>&1
```

Progress in another terminal:

```sh
tail -f ~/Projects/muse-guard/study_runs/holdout-restart-2026-10-27/progress.log
```

Estimate: prior clean pilot 758.317 seconds / 12 flows × 160 = 10,110.9 seconds = **2.81 hours**. The two conflict smoke flows used mean initial time 46.05 seconds, mean repair time 65.82 seconds and a 3.03-second card. With 80 solvable and 80 impossible flows, a rough extrapolation is 160 × 46.05 + 80 × 65.82 + 40 × 3.03 = 12,755 seconds = **3.54 hours** (only two dev flows, so uncertain). Allow **3–5 hours**, with a ceiling of roughly 20 hours if all 240 potential coding attempts consume their 300-second timeout, plus card/export overhead. This is a planning estimate, not a promise. Caffeinate covers the executing process. No public publication is included.

Summary reports counts/denominators/distinct tasks and separate reminder export warnings. A stopped cohort remains incomplete, not a null result. Provider receipts are the cost authority; main-session exports remain required for main steps/messages. Guarded cards count as separate overhead. The old h13-b exclusion still counts toward the monetary cap.
