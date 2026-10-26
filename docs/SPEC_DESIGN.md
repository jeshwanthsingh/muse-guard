# Spec to rules — separate feature, 2026-10-26

No existing study module, launcher, dataset or manifest changes. New spec_guard/
package and opt-in spec_guard/bin/muse-guard wrapper. Existing named-task commands
delegate unchanged; custom confirmed-rule files use a separate adapter. The new
adapter can check a supplied candidate offline and optionally author through the
existing sandbox/gateway utilities without admitting custom tasks to the study.

1. Strict proposal schema: small typed input domains (<=8 values each, <=6 fields,
   <=256 combinations), <=16 rules, eq/gte conditions, string actions, exact full
   sentence quotes. An optional quoted default is reviewed like any other rule.
   Missing defaults remain explicitly unspecified; do not invent behavior.
2. Keep every candidate item with validation errors and review decisions. Mark
   unrepresented source sentences as unconverted/context for review. Only valid,
   explicitly confirmed items enter the table. Exact quote presence proves source
   linkage, not semantic accuracy. The human must review condition/action meaning.
3. Enumerate every input and every differing-action rule pair. Report all witnesses,
   never trust model conflict claims. JSON-compatible YAML matches the task schema.
   Record doc/proposal/confirmed hashes, full source, model, review and coverage.
4. Static spec viewer: highlighted source, side-by-side rules, rejected/unconverted
   items, verified clashes. Fake demo clearly labeled; no live model calls today.
5. Eight hand-authored docs/truth tables and explicit clash lists are preregistered
   before real evaluation. No automatic repair of failed extractions or retries.
   Evaluation uses the original proposal, before human rejection can hide mistakes.
6. Live calls require --real and date >=2026-10-27; shared ledger lock and $5 cap,
   max6144 tokens reserved per extraction, max2048 output, actual provider usage.
   Missing usage retains reservation and stops the batch. Fake calls never write
   the shared cost ledger. Unit tests cover validation, review, search, budget and
   read-only use of existing independent checker. Full tests and freeze byte checks.
