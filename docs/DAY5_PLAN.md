# Day 5 implementation and verification plan

Contract: user's Day5 request and approved Day4 fair-recovery amendment. Native
execution with offline tests first; Day4 pushed normally, Day5 local only.

- [x] Prove same-session continuation offline using real Muse echo exports.
  Repeated muse exec --session-id preserves history (observed two turns).
- [x] Add plain adapter: retain isolated workspace/HOME, use exact normal follow-up,
  never materialize v2 or a verified witness for that agent. Score afterward against
  approved-v2 expectations while preserving actual agent-side rules as runtime data.
  Record test edits independently. Test no-edit interpreter does not gain a pass
  just because the checker knows approved v2; preserve existing planted-cheat checks.
- [x] Add dollar quota at gateway, after explicit user delegation of the choice.
  Reserve exact counted uncached input plus worst-case output before each request,
  settle with provider usage; missing usage retains reservation and stops admission.
  Keep 12 steps/320k tokens/300s and the original shared $5 ledger. No old uncertainty
  is deleted. Unknown/unresolved prior spend remains blocking. Test tiny remaining
  allowances, cache settlement, missing usage and concurrent request serialization.
- [x] Predeclare pilot: retry, refund, shipping; both twins, both modes, one repeat.
  Same B decision; fixed recorded mode order seed. Dev only, never holdout. Record
  every initial, card and repair; stop on cap, preserve incomplete/censored attempts.
- [x] Viewer: existing cool palette/system type. Add truthful five-step progress,
  actual export conflict text (trim only), human title + small ID, compact clash
  summary with full card disclosure, selected replay choice, v1->v2 changes,
  measured before/after behavior and collapsible code diff without blank padding.
  Actual sandboxed observations run outside page request; viewer only reads them.
  Missing observation/export evidence is unavailable, never invented.
- [x] Test actual render, escaping and evidence order; real browser 1280x720
  screenshots, download match and no console errors. No verdict logic in viewer.
- [x] Full offline suite, clean-checkout checks, code review, privacy and gitleaks.
  Update contributions and report pilot spend plus cached/uncached study math.

Scope notes: raw session exports/artifacts remain ignored. Public records save only
selected agent text and bounded observations. Historical scores, original holdout
bytes, both existing manifests and old ledger evidence are preserved. No study.
Runtime changes invalidate the previous active runtime lock; do not treat that
manifest as covering new code, or enable holdout execution without a new freeze.

Execution limitations: all twelve planned flows have a recorded outcome/stop, but
this is NOT a completed valid fair-comparison pilot. Seven flows precede the
isolation fix; one was interrupted, three hit nested-sandbox infrastructure failure,
and one was quota-blocked without inference. Final-code paid validation remains
blocked by the shared daily cap. Cost projections are explicitly provisional.
