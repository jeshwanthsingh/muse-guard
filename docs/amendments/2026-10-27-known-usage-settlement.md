# Known-usage settlement correction — 2026-10-27

Authorized before the single corrective dev flow; no holdout runs. Preserve
Day6 ef9d36b and the original Oct27 cohort, including the plain shipping failure.

## Evidence and cause

Repair shipping-impossible-v2-3c5f60d5f05a, request 5: counted input 6929;
requested maximum output 2048; actual input 6786; actual output 2120; cached 0.
Per-request estimate $0.01736525; actual $0.01749250; excess $0.00012725.
The previous four calls cost $0.02496115, so total measured phase cost was
$0.04245365 against a $1.36 allowance. Offline replay reproduces
“Provider usage exceeded request reservation”, then unknown=True and five
subsequent “Prior provider usage is unresolved” refusals. The journal's generic
policy/budget labels obscured the cause. The provider exceeded the requested
output limit; the harness incorrectly treated fully known, affordable usage as
missing. This contributed to invalidating the run. It does not prove the agent
would otherwise repair: its final response separately refused because v1 files
remained contradictory. No explicit success claim was contradicted.

## Narrow correction

Use submission_tools.settlement.ReconciledGateway for the corrective flow.
The same admission, model, shared daily ledger, token/step/time ceilings and
$1.36 phase reservation remain. Known usage is settled against the already
reserved phase allowance. Per-request overruns are journaled explicitly, not
called unknown. Actual token totals reconcile the conservative token counter.
Missing usage, exhausted allowance, malformed usage, or a provider overrun
beyond the whole phase quota stop further admission. No budget is increased.
As with any client cap, enforcement relies on provider billing/usage behavior;
a provider violating an entire reserved quota cannot be retroactively uncharged.
The correction will apply identically to both modes in any later approved study.

## One corrective flow, not a replacement result

User authorized one fresh shipping-impossible/plain dev flow with the same
session-continuation protocol and Rule B decision. No other pilot flow is rerun.
No prompt or scoring change. Run on committed submission code with the explicit
gateway override; record runtime commit, patch hashes and linked phase hashes.
Do not describe it as an unchanged Day6 execution. Shared Oct27 $5 cap remains.

The original frozen gate continues to reject the original cohort. A supplemental
gate uses the existing freeze_ready checks on a derived 12-entry view replacing
only the identified faulty flow, and reports both original and corrected views.
A failure without infrastructure/budget faults is a valid outcome, not grounds
for another rerun. If correction evidence still fails, stop and report it.

No study or reviewed-freeze commit is authorized. Once the corrected gate passes
and the user confirms, a later study may use a separately enforced one-time $70
hard cap, distinct from the $5 daily cap. That future cap is not enabled here.
