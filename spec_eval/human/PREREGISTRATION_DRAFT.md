# External-authored spec evaluation — preregistration DRAFT, 2026-10-27

Pending user answer-key review. No freeze and no real extraction runs on this set.
Separate from the original eight-document evaluation and the frozen coding study.

Provenance: user identifies the two documents as written by an independent AI
(Claude), reviewed by the user. Codex drafts keys; user corrects/approves them.
No claim of human authorship, blind adjudication or statistically independent
model errors. The folder name human is a user-specified path, not an authorship claim.

After corrections: freeze source docs, approved JSON keys, explicit source/support
links, action aliases, prompt, evaluator and this final protocol with SHA-256 hashes
in a NEW separate manifest before any extraction. Retain the original manifests.
Order doc1 then doc2; one Standard Muse Spark extraction each; no retries or
post-result changes. Ground truth never enters model input. Keep the existing
extraction prompt/model/budgets; report limitations such as cross-sentence scope.

Score initial proposals before manual rejection. Report per doc correct/wrong/
missing rules, domain match, found/missed/false clashes, actual tokens and cost.
Wrong extraction is failure. Confirm action aliases before calls; no post-hoc
alias expansion. Exact sentence matching must preserve multiline source quotes;
any whitespace normalization policy must be fixed and tested before freezing.

The original evaluator unconditionally expects a fallback. Package doc2 has none,
so a separate scorer must support an absent fallback without inventing one or
changing the original evaluator. Preregister how equivalent disjoint rules,
explicit exceptions and redundant prohibition sentences count, then test the
separate scorer offline before running. No changes to protected study/spec paths.

Use the canonical results ledger and shared $5 cap. Each extraction reserves
$0.026112 (6144 tokens × $4.25/M); two reserve at most $0.052224, not another daily
allowance. Actual usage determines actual spend. Stop on unknown usage or cap.
The Oct27 prior total is $1.64741640; re-read ledger at execution time.

Report this set separately with its Claude/user-review provenance, even when both
docs have no clashes. Do not pool its scores into the original eight-doc totals.
