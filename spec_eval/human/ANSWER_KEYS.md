# Approved answer keys — 2026-10-27

The user corrected and approved the draft before any extraction.
Machine-readable rules tables and explicit witness lists are in
[doc1](truth/doc1.json) and [doc2](truth/doc2.json).

Doc1 uses four Boolean fields: posting_over_30_days, top_company,
applied_over_3_weeks, heard_back.

| Rule | Condition | Action |
|---|---|---|
| A | posting_over_30_days=true | stale |
| B | top_company=true | active |
| C | posting_over_30_days=false, top_company=false, applied_over_3_weeks=true, heard_back=false | follow_up |
| Default | no rule matches | wait |

Clashes: A stale versus B active at old=true/top=true with
(late,heard_back)=(false,false), (false,true), (true,false), (true,true).

Doc2 fields: perishable, resident_away, needs_signature, oversized.

| Rule | Condition | Action |
|---|---|---|
| A | perishable=true, resident_away=true | return_to_sender |
| B | perishable=true, resident_away=false | notify_resident |
| C | perishable=false, needs_signature=true | hold_at_desk |
| D | perishable=false, needs_signature=false, oversized=false | put_in_locker |
| E | perishable=false, needs_signature=false, oversized=true | hold_at_desk |

Clashes: none. All 16 inputs covered; no fallback invented. See preregistration
for exact equivalence/alias policy, original quotes, and provenance. The earlier
DRAFT files are retained as superseded history and are not the frozen keys.
