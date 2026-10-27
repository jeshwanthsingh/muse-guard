# Separate Claude-authored, human-reviewed set — preregistered 2026-10-27

Final protocol before any real calls. User approved the corrected keys, doc1
wording edit, doc2 scope and separate optional-fallback scorer in this chat.
Authorship: “written by an independent AI (Claude), reviewed by me” (the user).
Keys drafted by Codex, corrected/approved by the user. Not a blinded human study.
The directory name human is not a claim of human document authorship.

## Corpus and scoring

Order: doc1, doc2, exactly one Standard muse-spark-1.3 extraction each.
Doc1 A/B are unconditional and have four conflicts. Doc2 has zero conflicts
and complete coverage without a fallback. Source/keys live beside this file;
WORDING_CHANGE.md records the pre-run user correction. The original eight-doc
set, scorer, manifest and results are unchanged and remain reported separately.

Use the original frozen provider prompt, models and 6144-token/2048-output
admission limits. Send only the actual source document, never truth/aliases.
No retries, prompt changes, answer-key changes or alias changes after outcomes.
Raw proposals are retained. Model proposals are scored before human rejection.

Primary per-document results: rules correct/wrong/missing, domain correctness,
clashes found/missed/false, and extraction success. Wrong extraction is failure.
Include fallback in rule counts only when the source has one: doc1 four
behavioral entries (three rules + fallback), doc2 five rules and no fallback.
An invented fallback is wrong. Missing required rules cannot be hidden by the
absence of a fallback. Proposed same-action overlapping rules are still scored
by their matching input sets, not automatically counted as conflicts.

Rule equivalence requires source sentence, action and the same matching inputs
over the complete truth domain. Explicit field/action aliases are fixed in
truth/doc1.json and truth/doc2.json BEFORE calls; names outside these lists are
not manually forgiven. Field-alias collisions fail. Typed domain values must
match; order is irrelevant. Duplicate rules use multiset counts.

Normalize whitespace within paragraphs and source quotes only; preserve all
words, case and punctuation. This accommodates the supplied line-wrapped prose.
Source quotes must match complete normalized source sentences. Do not infer
priority. A/B conflict in doc1 despite natural-language temptation to resolve it.
Doc1's no-top-company-follow-up sentence supports C's explicit exclusion, not a
fifth output rule. Doc2 E inherits non-perishable/no-signature scope from D;
its matching-input set is frozen accordingly. Supporting-source links retained
in keys are reviewer rationale, not supplied as hidden hints to the model.

## Freeze and limits

MANIFEST.json hashes both docs, approved keys, this protocol, wording history,
separate scorer/tests and all original extraction dependencies. Commit the
manifest before real calls; evaluator verifies hashes before each call. New
implementation is entirely outside protected paths. Report separately; never
combine with the original eight into a single success rate.

Use canonical results ledger/lock and the shared Oct27 $5 allowance. Two calls
reserve at most $0.052224 together; actual receipts determine spend. Original
remaining allowance was $3.35258360; reread it after the corrective pilot flow.
Unknown usage or insufficient allowance stops execution. Retain stopped
attempts, no replacement. No future study or $70 allowance is enabled here.

Command after commit: python3 -m submission_tools.human_eval --real --out
spec_eval/human/results/2026-10-27. The fixed date is 2026-10-27.
