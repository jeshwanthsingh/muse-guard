# Submission preparation — 2026-10-26

Local branch codex/submission starts at 03b558b. No push, merge or paid calls.
The submission tree includes the recorded demo and spec feature; it is NOT the
runtime for tomorrow's frozen coding experiment.

The required pilot/study runtime is day6 at
`ef9d36b0e4cf546d45cae469fb61d5d69f27a80e`. Follow docs/NEXT_PILOT.md on that branch.
Never infer that the later submission tree matches an older study manifest.
A clean pilot and reviewed refreeze are still required before any holdout study.
No holdout execution is authorized by these preparation commands.

## Protected paths

`python3 submission_tools/check_protected.py` checks both worktree and Git index
against immutable blobs at 03b558b, verifies manifest coverage, and rejects new
files matching the freeze's directory patterns. It also protects the separate
spec evaluation manifest/source. `submission_tools/protected.json` identifies the
baseline; changing its hashes does not bypass comparison to Git objects.
A local `.git/hooks/pre-commit` runs the check on codex/submission before every
commit. Hooks are local enforcement and can be bypassed deliberately; they are
not a security boundary or a new reviewed study freeze.

## Day6 provenance without invalidating original evidence

The original pilot already records its source revision in the cohort. Its phase
and recovery records are hash-linked. Adding metadata directly to those files
would break the links, so use immutable provenance envelopes: every newly written
or changed result is copied with runtime_commit, original_sha256 and the original
JSON. Existing result files are never rewritten. Keep these envelopes alongside
the original results and always include both in study reporting.

Before switching branches tomorrow, copy the standalone wrapper outside the repo:

```sh
cd ~/Projects/muse-guard
python3 submission_tools/check_protected.py
cp submission_tools/study_receipts.py /tmp/muse-study-receipts.py
git switch day6
git status --short
python3 /tmp/muse-study-receipts.py --checkout "$PWD" --out ../muse-guard-pilot-receipts-2026-10-27 --verify-only
python3 -m unittest discover -s tests -q
./muse-guard gate --split dev
python3 scripts/clean_pilot.py --plan
set -a
. ./.env
set +a
python3 /tmp/muse-study-receipts.py --checkout "$PWD" --out ../muse-guard-pilot-receipts-2026-10-27 --execute-pilot
python3 scripts/clean_pilot.py --summary results/CLEAN_PILOT_2026-10-27.json
```

The wrapper runs the EXACT existing `scripts/clean_pilot.py --execute` command,
checks branch/commit/source before and after, and writes provenance envelopes even
if the command fails. The receipt directory must be new and outside the checkout.
The original date/budget/order/source gates still apply. Stop and review as directed
in NEXT_PILOT.md. For a later authorized study executor, use the same verification,
before/after snapshot and envelope capture functions; no study executor is added here.

## Rebuild the presentation

```sh
python3 submission_tools/check_protected.py
python3 submission_tools/export_demo.py --out /tmp/muse-submission-demo
```

Use a new output directory. The wrapper calls the frozen exporter then changes
only index labels/layout/CSS and the output hash manifest. Downloadable evidence
is byte-identical to the original static demo. The allowed public GitHub link is
navigation only; loading the page performs no network requests.

## Baseten

See [the preregistered exploration](BASETEN_EXPLORATION.md). The supplied grant
uses the shared Model API and restricted `meta-models/muse-spark-open-1026` name.
Offline bridge tests pass. Live comparison remains blocked on a verified token
counter and balanced executor; do not represent fake tests as a
live adapter validation. Tomorrow's preflight reports this blocker without calls.


## Review correction — 2026-10-26

The approved [behavior-only recovery amendment](amendments/2026-10-26-behavior-only-recovery.md)
supersedes the older strict recovery criterion. Keep Day6 raw results, then apply
the external scorer and reviewed supplemental freeze described in [CONTINUOUS.md](CONTINUOUS.md).
Test edits are descriptive in both modes, not recovery failures. The current
continuous demo also shows exactly what its finite checks do and do not cover.
