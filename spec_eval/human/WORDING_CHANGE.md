# Pre-registration wording correction — 2026-10-27

At the user's explicit request, doc1 changed:

Before: “Anything at one of my top companies stays active, no matter what.”

After: “Anything at one of my top companies stays active.”

Reason: remove ambiguous priority wording. The user confirmed A and B should
be unconditional, giving four stale/active clashes when old=true and top=true,
for every combination of applied-over-three-weeks and heard-back. No extraction
was run on either version before this change. Doc2 scope and zero clashes were
confirmed. Provenance remains Claude-authored, user-reviewed.
