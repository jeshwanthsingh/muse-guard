# Static recorded demo

Open output/judge-site/index.html directly in a browser. The checked-in example
contains the refund recovery, retry recovery, a solvable refund PASS, and an
explicitly planted edited-test cheat. Every page says Recorded run. Historical
examples are development evidence, not a completed study or a new clean pilot.

To export another selection into a new folder:

```sh
./muse-guard export-site \
  demo/records/refund-recovery.json \
  demo/records/retry-recovery.json \
  demo/records/solvable-pass.json \
  demo/records/planted-cheat.json \
  --out output/judge-site-preview
```

Run IDs in results/ are also accepted. Existing output directories are refused.
Copy the whole output folder to retain its relative links. No server or JavaScript
is needed. The evidence button downloads JSON through an inert data URL so Chrome
also downloads from file URLs; its bytes match the separately linked JSON file.

Only allowlisted evidence fields are exported: task rules, recorded outcomes,
checks, decisions, measured cost, selected agent explanation, saved behavior and
an attached repair diff. These are explicitly labeled public evidence extracts,
with a SHA-256 of the selected source file. Session IDs, environment variables,
request journals, child-session links and raw logs are excluded. Unknown fields
are not copied. Suspicious credential, private-path, URL and hostname patterns
reject the export before publishing the output directory. Scan any new selection
with gitleaks as well; pattern checks cannot recognize every arbitrary secret.

The curated records were prepared offline with scripts/prepare_static_demo.py.
It preserves the historical ledger, verifies frozen solution/rule hashes before
saving additional display observations, and checks a newly constructed planted
cheat. Regeneration requires deliberately choosing/removing those curated files;
the script refuses to silently overwrite them. The exporter itself never reads
raw sessions, runs candidates, changes a verdict or contacts a model.

.github/workflows/pages.yml contains a manual-dispatch deployment template with
its job hard-disabled by `if: ${{ false }}`. There is no push trigger. Pages has
not been enabled or deployed. A later explicit publication approval is required
before changing the job condition or configuring repository hosting.

Verification: offline renderer/privacy/link tests; real Chrome at 1280x720 using
file URLs; all four evidence downloads matched JSON bytes; no network requests,
live controls or horizontal overflow. Screenshots are under output/playwright/
with the static- prefix. Final test counts and privacy evidence are recorded in
results/STATIC_DEMO_VERIFICATION.json.
