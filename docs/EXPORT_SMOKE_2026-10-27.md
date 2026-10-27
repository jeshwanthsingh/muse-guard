# Export amendment smoke results — October 27, 2026

Two DEV refund-impossible flows only. Both recovered; no paid call was repeated. No holdout call occurred. The two-flow process was NOT uninterrupted: a diagnostic JSON list mistakenly placed in results/ caused a ledger enumeration exception after the plain repair had completed. Original traceback/cohort are preserved in docs/evidence; full private traceback is in results/raw/export-smoke-bookkeeping. The list was moved out; the completed same-session plain repair was attached from its saved receipt, and only the unstarted guarded flow was executed. No runtime was patched between the two flows.

| Mode | Phase | Outcome | Main steps | Actual cost | Failed reminder exports |
|---|---|---|---:|---:|---:|
| plain | attempt | CONFLICT VERIFIED | 5 | $0.09609670 | 4 |
| plain | repair | PASS | 8 | $0.14010010 | 10 |
| guarded | attempt | CONFLICT VERIFIED | 5 | $0.09285345 | 4 |
| guarded | conflict_card | GENERATED | N/A | $0.00194025 | 0 |
| guarded | repair | PASS | 5 | $0.07075015 | 4 |

All four root exports succeeded. All root and reminder export diagnostics files exist; all five phase journals match gateway events, actual tokens and cost. Visible/hidden approved-v2 repair checks pass in both modes. Missing reminder logs did not trigger a policy stop. This is evidence for the export amendment, not an uninterrupted smoke-cohort claim.

Smoke cost: $0.40174065. Shared daily total: $2.19039485 / $5, fully accounted. Study ledger remains $0.1083648 / $70; $69.8916352 remains. Combined known spend today: $2.29875965.

Offline checks: 25 tests across export policy, restart, prior holdout orchestration, and corrected settlement. Local loopback permission was required for the fake-transport settlement test. Old activated freeze and 103 protected files remain unchanged. The new draft is not activated.
