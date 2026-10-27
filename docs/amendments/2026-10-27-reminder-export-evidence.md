# Reminder-export evidence amendment — October 27, 2026

Shown to the developer before committing. Local only; no holdout execution authorized.

Root-session export success and complete, valid provider-journal usage remain mandatory. Failure to export a linked reminder session is recorded with its session ID, exit code, full stdout and stderr, but does not stop a flow when those mandatory records are complete. Reminder exports remain supplementary evidence; missing exports are never treated as zero usage. Root-export failure, unknown or invalid provider usage, and all other existing infrastructure stop conditions still stop execution. Main-session steps retain their existing definition; reminder requests, tokens and cost remain included through provider receipts. No task, prompt, behavioral score, decision, limit or primary measure changes.

The interrupted h13-b attempt remains preserved and is reported separately as **excluded: harness stop**. Its $0.1083648 remains charged to the one-time $70 allowance. A newly reviewed freeze and explicit authorization are required before a new cohort runs the exact same 160 assignments in the exact same order. No holdout calls are authorized by this amendment.

## Evidence and implementation

Re-exported exactly the five failed saved reminder IDs, without model calls. Each returned exit 1: `export failed: no retained session log found for session <id>` and suggested a session.jsonl path. No matching session.jsonl exists under the retained isolated root. This proves unavailable retained logs, not whether Muse never retained them or removed them. There is no evidence of a lock or transient timing failure. Full diagnostic stdout/stderr are preserved privately under the stopped run's raw/export-diagnosis directory.

PRIMARY_MEASURES.md item 5 explicitly defines main Muse steps, all reminder costs and provider request counts. muse_guard/evidence.py extracts main steps and assistant messages from the root before child exports are merged. Independent checker records supply behavior, test inventories and edit evidence. The provider journal for the stopped attempt contains all 14 requests and $0.1083648; partial exports contain only $0.0490361. Child exports are therefore supplementary, not required to compute registered primary measures.

The new version is submission_tools/export_runtime plus export_policy.py. Old runtime and manifests are unchanged. Full export stdout/stderr go to private files, including timeout diagnostics; structured records reference those files and preserve exit codes. Before continuing, the policy requires the persisted journal to match admitted gateway events, validates every receipt, and reconciles recorded tokens and cost. Root failure, missing usage and gateway blocks remain fatal. No export retry is added to execution.

Validation: two offline-tested DEV refund-impossible flows, plain then guarded, under the shared daily $5 cap and matched 12-step/320k-token/300-second limits. Rule B wins in both. These are smoke tests only, excluded from all study estimates and comparisons. No holdout call occurs. Source hashes and all phase receipts are saved.

Restart plan: new cohort holdout-restart-2026-10-27, 160 original holdout rows unchanged. A draft freeze will bind amended code and smoke evidence and retain the prior manifest. Activation and execution require a later explicit confirmation. Retain the prior excluded attempt separately and subtract its cost from the $70 allowance, leaving $69.8916352 before the restart; smoke uses the daily ledger instead. Do not reinterpret missing reminder exports as missing billed calls.
