# Separate external-authored set: DRAFT answer keys — 2026-10-27

Not approved, frozen or evaluated. Source files were absent in the checkout;
reconstructed from the user's pasted text, preserving the supplied line wraps.
Authorship label supplied by user: written by an independent AI (Claude), not
muse-guard's author, reviewed by the user. Do not label human-written unless the
user confirms rewording. Answer keys below are drafted by Codex for user correction.
This is externally authored, user-reviewed input; not a blinded or independent
human ground-truth adjudication.

## doc1: Job tracker — proposed exception-aware interpretation

Fields, each with domain [false, true]: posting_over_30_days, top_company,
applied_over_3_weeks, heard_back. All 16 combinations are declared inputs.
Actions are mutually exclusive outputs: stale, active, follow_up, wait.

| ID | Source sentence (line breaks collapsed for display) | Condition | Action |
|---|---|---|---|
| A | If the posting is more than 30 days old, mark it stale. | posting_over_30_days=true AND top_company=false | stale |
| B | Anything at one of my top companies stays active, no matter what. | top_company=true | active |
| C | If it's been over 3 weeks and I haven't heard back, send a follow-up, but only for postings that aren't stale and aren't at a top company. | posting_over_30_days=false AND top_company=false AND applied_over_3_weeks=true AND heard_back=false | follow_up |
| Default | Otherwise, just wait. | no rule matches | wait |

A's top_company=false restriction comes from B's explicit “no matter what”
exception, not from A alone. This needs user approval. The sentence “For top
companies I follow up myself, so the tracker shouldn't.” is a prohibition already
encoded in C's top_company=false restriction; it is not an additional next-action
rule. Retain it as supporting source evidence, not a silently dropped requirement.

Clash list under this proposed interpretation: []. Coverage: active 8 inputs,
stale 4, follow_up 1, wait 3. Exactly one output on all 16 inputs.

Alternative if the user intends both A and B to be unconditional: A only checks
posting_over_30_days=true. A/B then require stale and active on these FOUR inputs:

| posting_over_30_days | top_company | applied_over_3_weeks | heard_back | Rules/actions |
|---|---|---|---|---|
| true | true | false | false | A stale / B active |
| true | true | false | true | A stale / B active |
| true | true | true | false | A stale / B active |
| true | true | true | true | A stale / B active |

Do not freeze either reading before the user resolves this distinction.

## doc2: Package room

Fields, each with domain [false, true]: perishable, resident_away,
needs_signature, oversized. All 16 combinations are declared inputs.
Actions: return_to_sender, notify_resident, hold_at_desk, put_in_locker.

| ID | Source sentence (line breaks collapsed for display) | Condition | Action |
|---|---|---|---|
| A | If it's perishable and the resident is away, return it to the sender. | perishable=true AND resident_away=true | return_to_sender |
| B | If it's perishable and the resident is home, notify the resident right away. | perishable=true AND resident_away=false | notify_resident |
| C | For anything that isn't perishable: if it needs a signature, hold it at the front desk. | perishable=false AND needs_signature=true | hold_at_desk |
| D | Non-perishable packages that don't need a signature go in a locker, unless they're oversized. | perishable=false AND needs_signature=false AND oversized=false | put_in_locker |
| E | Oversized ones get held at the desk too. | perishable=false AND needs_signature=false AND oversized=true | hold_at_desk |

E inherits the non-perishable/no-signature scope of the immediately preceding
sentence. It does not override perishable handling. This scope needs user approval.
No fallback sentence exists, and none is invented: the five rules cover all inputs.
Clash list: []. Coverage: return_to_sender 4, notify_resident 4, hold_at_desk 6,
put_in_locker 2. Each input matches exactly one rule in this normalized table.

## Review before freezing

Confirm/correct: doc1's top-company exception; doc2's oversized scope; field/action
names; treatment of doc1's redundant no-follow-up sentence; the authorship label.
Both docs are conflict-free under the proposed readings. Do not add a positive
case, change wording or choose another interpretation merely to balance results.
The frozen answer keys must preserve exact original source quotes, with explicit
supporting-source links for cross-sentence exceptions and scoped references.
