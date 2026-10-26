# Static judge demo — 2026-10-26

Contract: export selected recorded runs as a self-contained folder, openable via
file URLs or static hosting. Reuse the viewer presentation with a static mode;
no client script, decision controls, provider calls or runtime server are shipped.
The default output is output/judge-site; --out selects a new output folder.
Existing output is refused, so an export cannot overwrite unrelated files.

Steps and proof:
1. Add public-evidence projection and privacy checks. Unknown/session/environment
   fields are excluded; suspicious content in selected fields fails closed. Tests
   cover secret/path injection, traversal, duplicate records and untouched sources.
2. Add export-site CLI and static viewer mode, index, relative evidence downloads.
   Test HTML links, labels, fixture distinction and absence of live controls/code.
3. Prepare four offline demo records from historical refund/retry/PASS evidence
   and a freshly checked planted cheat. Preserve original ledgers and scores.
4. Add a manual-dispatch workflow with the deployment job hard-disabled. Build
   locally, scan the output with gitleaks, browse file URLs at 1280x720, and capture
   index/recovery/PASS/planted screenshots. Commit locally on the new branch.

Public evidence is explicitly an extract, not the complete private source record.
Store the source SHA-256 for provenance. Actual verdicts/costs remain unchanged;
planted results are never presented as observed Muse behavior or study evidence.
No hosting setup, paid calls, pilot, holdout model runs, push or merge.
