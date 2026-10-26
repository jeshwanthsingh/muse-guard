# Run locally

Requires Python 3.11+ on Linux or macOS. No Python packages are required.
Linux compatibility is by design; the current verification host was macOS.

```sh
python3 -m unittest discover -v
python3 -m muse_guard.runner --task all
```

The second command creates six preflight ERROR records when no environment key is
available. That does not run Meta or measure model behavior. Existing JSON records
are retained with unique IDs. Do not run two Python API callers concurrently;
the command-line entry point takes a filesystem lock for serial accounting.

## Before a paid run

Supply `META_API_KEY` through the process environment, never a command argument,
tracked file, chat message, or committed shell script. The runner does not load
.env files or use stored browser/keyring credentials. It isolates HOME/config and
passes the key only to Muse; candidate checker children receive no credentials.

The operator must first configure and verify an isolated key/team's enforceable
remaining daily spending cap at Meta, at most $5, and Standard mode. If the billing
console has no enforceable cap, do not use this attestation path: live work stays
blocked until request-level token limits or a budget-enforcing proxy are built.
A notification threshold or payment threshold is not a spending cap.
Once that enforcement actually exists, set `MUSE_GUARD_DAILY_LIMIT_USD` to the cap
and `MUSE_GUARD_STANDARD_CONFIRMED=1` in the environment. These are attestations,
not a programmatic proof of the provider's billing configuration. CLI step limits
and local accounting alone do not guarantee the $5 ceiling. No paid calls were
made during Day 1.

The runner pins `muse-spark-1.3`, passes `--contributor-mode off`, six model steps,
no web tools, no foreign personal context, and disables the model-based approval
judge. Tool approval prompts are disabled only inside the throwaway workspace;
Muse's filesystem sandbox stays enabled. Default user hooks, settings and saved
credentials are excluded through a fresh HOME/config. Live checking of hostile
candidate code needs a container; this prototype does not provide one.

Installed Muse 1.4.2 does not support the documented Contributor-off flag.
The runner deliberately refuses to omit it. A CLI version supporting that flag
(or a separately verified equivalent Standard-only configuration) is still needed.

## Artifacts and accounting

`results/<task>-<unique-id>.json` includes requested mode, whether a model was
invoked, exit code, named checker rows, tokens, estimated USD cost, duration, and
frozen SHA-256 file hashes. Standard rates checked on 2026-10-26: $1.25/M uncached
input, $0.15/M cached input, $4.25/M output. Account invoices remain the billing
authority. The local ledger assumes these are the only calls using the capped key.

The runner exports the exact session, not `--last`:

```sh
muse export --session <session-id> --out <absolute-file-path> --redacted
```

The observed exporter writes one self-contained JSON document, schema v1, with
sessions, events, exporter version and diagnostics. Without `--out`, export prints
the absolute path to a timestamped trajectory JSON. With `--out`, it replaces the
named file atomically on success. Export is offline. Raw exports may contain code,
paths and personal context even with redaction; keep them in ignored `results/raw/`.

The meter supports the observed v1 `runtime.session` / `model_completed` usage
records, deduplicates source record IDs, and also accepts a normalized aggregate
for local protocol fixtures. It does not sum cumulative attribution/summary rows.
An unsupported or missing usage schema produces null tokens/cost and blocks the
next paid call. The meter has been verified on a zero-token echo export and on
nonzero local fixtures, not a billable Meta session. Final-claim extraction supports
the observed terminal envelope; it ignores unknown event schemas and tool output.

## Current CLI evidence

- `muse --version`: 1.4.2 (1.4.2-R4684.1); exporter identifies build b538db0a2c.
- Meta diagnostic, one model-step cap, Contributor-off flag: exit 2, unknown option.
- Credential diagnostic without that unsupported flag: exit 1, missing credentials.
- Export after those rejected attempts: exit 1, no retained session.
- Offline `--provider echo` diagnostic: exit 0; export exit 0, schema v1 file saved.
  Echo is a local protocol check, not a Standard Meta model result. Its event log
  includes a helper task configuration failure; exit 0 alone proves no task result.

See [CLI_CHECK.json](CLI_CHECK.json) for portable metadata. Raw local diagnostics
are kept under ignored `results/raw/cli-check/`.

Sources: [Meta authentication](https://dev.meta.ai/docs/muse-code/auth),
[headless execution and export](https://dev.meta.ai/docs/muse-code/extending),
[configuration](https://dev.meta.ai/docs/muse-code/configuration),
[Standard pricing](https://dev.meta.ai/docs/pricing-rate-limits).
