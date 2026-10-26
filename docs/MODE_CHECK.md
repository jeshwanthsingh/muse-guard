# Muse 1.4.2 mode check — 2026-10-26

- `muse --help` and `muse exec --help` do not list `--contributor-mode`.
  Passing it previously returned exit 2, unknown option.
- The installed 1.4.2-R4684.1 native binary contains neither the documented
  `MUSE_CONTRIBUTOR_MODE` string nor `contributor_mode`. This supports a version
  mismatch; string absence alone is not behavioral proof.
- The existing settings file contains only `schema_version` and `tui`; no mode
  setting was present. Credentials/auth files were not printed or copied.
- Meta's current docs say `MUSE_CONTRIBUTOR_MODE=0` disables Contributor for one
  run, and a headless run without a settings file defaults off. That per-run
  environment behavior could not be independently established for this binary.

## Reliable mode used here

Every live baseline uses an isolated HOME/config and requests
`MUSE_CONTRIBUTOR_MODE=0`, but the guarantee does not depend on CLI interpreting
that variable. `gateway.py` replaces the outbound model with `muse-spark-1.3`
(the documented Standard API model), supplies the real key only upstream, pins
its local model catalog to that model, and forwards only Responses requests to
the fixed Meta API origin. Muse receives a dummy credential. Contributor model
IDs, headers and alternative model choices are never forwarded. Each run JSON
records Standard mode and the actual forwarded model/request reservations.

The user permitted Contributor only for these synthetic toys if needed. That
fallback was not used; it grants no permission for real projects.

## Sources checked

- [Mode overrides and headless defaults](https://dev.meta.ai/docs/muse-code/subscriptions)
- [CLI configuration](https://dev.meta.ai/docs/muse-code/configuration)
- [Standard vs Contributor model IDs and prices](https://dev.meta.ai/docs/pricing-rate-limits)
- [Exact token counting](https://dev.meta.ai/docs/token-counting)

Standard Spark prices: $1.25/M uncached input, $0.15/M cached input, $4.25/M output.
The token-count endpoint includes context scaffolding and is used as a
conservative reservation, not as billed usage. Exported usage supplies actual
observed tokens; multiplying published rates gives the recorded cost estimate.
