# Day 4 design for review

Use the existing Python stdlib stack; no frontend build or external assets.
The task order is fairness audit -> amendment review -> implementation/tests ->
UI screenshot -> final re-freeze and local commits. Day3 is pushed; Day4 stays local.

## Viewer

muse-guard view <record id or JSON path> defaults to recorded replay. A local
loopback HTTP server renders task/rules, verified clash and explanation, A/B
buttons, repair diff, individual visible/hidden checks and evidence download in
that order. Large system sans text, cool white background (#f7f9fc), ink (#172438),
blue (#2454bb) for choices, gold (#fff0bf) for clashing rules, green (#146542)
for independently recorded passes. 1120px reading width at 1280x720; scroll for
later evidence. No external fonts, trackers or network assets.

Use --live only for an existing guarded AWAITING DECISION record. Decisions go
through a localhost-only, token-protected POST, reject replay/duplicate/unverified
choices, take the global run lock and reuse the recovery approval/repair functions.
Keys come only from the server environment, never HTTP or HTML. No automatic paid
calls from page load. Keep all verdict logic in existing checker functions.

Read stored repair_diff when available; otherwise derive it from hash-verified
local frozen solution artifacts. Missing artifacts show unavailable, never a
fabricated diff. Download returns the run JSON only. Escape all record content.
The browser cannot browse arbitrary files; the chosen record is the only resource.

## Protocol

Apply the accompanying Day4 amendment and matched ceilings. Preserve original
manifest bytes, add a versioned active manifest with its parent hash, and validate
the original data hashes when re-freezing. The fair same-session plain adapter is
an explicit study blocker; no study is executed or claimed today.

## Verification

Offline tests cover saved refund render/order/checks, hostile text escaping,
download bytes, replay rejection, verified live resume and duplicate/invalid
choices, budget refusal, retained manifest lineage and unchanged holdout bytes.
Use the actual local page in a browser at 1280x720 and save a screenshot.
