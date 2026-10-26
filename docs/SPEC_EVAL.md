# Spec extraction evaluation — preregistered 2026-10-26

Separate from the frozen coding study. Eight hand-written messy documents:
refunds, access, shipping, notifications, retention, bookings, pricing, support.
Their finite domains, source-linked rules/defaults and explicit clash lists were
written before any real extraction. Four docs clash and four do not; retention
has two conflicting input combinations. Fake responses are constructed harness
fixtures copied from these hand-written translations, never model evidence.

One Standard muse-spark-1.3 extraction per doc, in that order. No retries, no prompt
repair, no post-result changes, no ground truth in model input. Scoring uses the
original proposals before human rejection can hide extraction errors. The batch
uses --accept-all semantics for structurally valid proposals only. Real developer
confirmation is a local trust decision and not an external identity attestation.

Primary per-document and aggregate measures:
- Rules correctly extracted / ground-truth rules, including the quoted fallback.
- Wrong and missing rules, including invalid quotes/schema and dropped proposals.
- Clashes found versus the explicit ground-truth list; missed and false clashes.
- Extraction success only if there are no wrong/missing rules, all domains match,
  schema validation passes and no fabricated unconverted-source report exists.
  A wrong extraction is a failure even if it happens to find the right clash.

Rule equivalence requires the exact source sentence, matching action after ONLY
predeclared action aliases, and identical matching inputs over the complete truth
space. IDs and condition ordering are irrelevant. Duplicates use multiset counts.
Domains must match with typed values; extra/missing values count as failure.
Each clash is one concrete input plus an unordered pair of source quotes/actions.
All matching pairs at every input are counted. Context/domain-declaration sentences
are shown as not converted but are not extra ground-truth behavioral rules.
Action aliases are fixed in each truth file; no post-hoc semantic adjudication.

Snapshot corpus, prompt and separate feature source in spec_eval/MANIFEST.json.
Reject drift before the batch and each call. Keep failures and budget stops, never
replace them with successful retries. Missing usage stops the batch and retains
its reservation in the shared results ledger; completed-call cost is explicitly
partial until every call has a receipt. Cost/time/tokens are secondary measures.

Budget: use the same canonical results/.run.lock, daily results ledger and $5 cap
as the coding pilot. One extraction reserves at most 6144 tokens at $4.25/M =
$0.026112; eight reserve at most $0.208896 in total, not a separate $5 allowance.
The gateway counts input before forwarding and caps output at 2048 tokens. Actual
provider usage includes cached input. At 800 input + 450 output tokens, the
illustrative cost is $0.0029125/call or $0.0233 for eight; this is an estimate, not
a receipt. Standard rates: $1.25/M input, $0.15/M cached input, $4.25/M output,
checked against https://dev.meta.ai/docs/pricing-rate-limits on 2026-10-26.

Exact command on October27, after loading the key privately:

```sh
cd ~/Projects/muse-guard
set -a
. ./.env
set +a
PATH="$PWD/spec_guard/bin:$PATH" muse-guard spec-eval --real --out spec_eval/results/2026-10-27
```

The live evaluation refuses any date except 2026-10-27. General live spec/code
calls refuse dates before 2026-10-27 and require explicit --real. Do not reset the
ledger. If the coding pilot has consumed the budget or left unknown usage, stop.
No real extraction, coding, pilot or holdout calls were made during implementation.
