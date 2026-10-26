# Day 4 implementation plan

Goal: approved fair-recovery amendment, matched limits and a local evidence viewer.
Architecture: existing Python stdlib runner/checker; separate loopback display server.
Spec: docs/DAY4_DESIGN.md and approved docs/amendments/2026-10-26-day4-fair-recovery.md.
Execution: native in this session, per user approval. No study or paid model calls.

- [x] Tests first: viewer order, stored verdict, escaped content, replay POST refusal,
  download bytes, verified live continuation, duplicate choices and budget stop.
- [x] Implement muse_guard/view.py + static viewer assets and CLI view subcommand.
  Extend guarded recovery only with an awaiting-record continuation entry point.
  Verify with offline fixture tests and existing full suite; do not change checker.
- [x] Apply approved 12-step / 320000-token / 300-second limits to both modes;
  block initial-only plain from holdout use until a fair same-session adapter exists.
  Test limits and pre-paid holdout refusal.
- [x] Render refund recovery at 1280x720 in real browser; inspect all sections and
  evidence download, save screenshot. Live continuation uses offline fixtures only.
- [x] Preserve original manifest; add amended manifest with explicit lineage and
  unchanged data hashes, anchor to its creation commit. Test old-manifest tamper,
  original-data drift and amended-protocol drift refusal.
- [x] Review complete diff; run final offline suite, privacy scan, gitleaks; commit
  locally, re-freeze after runtime settles, verify GitHub day3 and no day4 push.
- [x] Update contributions and final simple report including zero Day4 cost.

Review focus: untrusted record HTML; localhost request forgery; duplicate approval;
missing frozen artifacts; historical verdict preservation. Tests own each case.
