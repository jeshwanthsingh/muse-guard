# Spec → rules (separate extension)

The root launcher and study CLI are freeze-pinned. Keep them unchanged. Opt into
the new wrapper for this feature:

```sh
cd ~/Projects/muse-guard
export PATH="$PWD/spec_guard/bin:$PATH"
muse-guard spec spec_eval/docs/refunds.md --response spec_eval/fake/refunds.json --accept-all --out spec_runs/refund-demo
```

Without --accept-all, each structurally valid rule shows its exact source sentence
beside the condition/action and asks y/n. Invalid proposals remain visible as
couldn't convert and cannot be accepted. Unrepresented sentences remain visible
as context/unconverted, never silently disappear. --accept-all is an explicit
scripted confirmation, not semantic verification of the English translation.

Output: record.json (source, hashes, model, every proposal/error/decision),
confirmed.yaml (JSON-compatible YAML, same id/rules/when/action/input_space shape
as tasks), and an offline index.html viewer. The viewer highlights source
sentences and lists every differing-action pair at every matching input. It
clearly labels fake responses. No coding agent is invoked during this command.

Finite limits: 1–6 fields, 1–8 typed values per domain, at most 256 combinations,
16 rules, eq/gte conditions. A quoted default is reviewed too. If none is confirmed,
unmatched inputs stay unspecified and coding is refused. No priority is inferred.
Exact source linkage is not proof of semantic accuracy; developers review the
translation, and the separate evaluation counts wrong extractions as failures.

Use the confirmed file without changing the study task catalog:

```sh
muse-guard run spec_runs/refund-demo/confirmed.yaml --out spec_runs/refund-preflight
# For a conflict-free spec, independently check a supplied solution offline:
muse-guard run spec_runs/shipping-demo/confirmed.yaml --candidate solution.py --out spec_runs/shipping-check
```

The adapter replays the confirmation receipt, refuses unresolved input coverage,
and stops on verified clashes before coding. It uses the existing independent
checker read-only, with distinct visible/hidden samples from the finite space.
Custom spec tasks are never inserted into the study's catalog. Named catalog
commands delegate to the original root launcher unchanged.

On/after October27, --real explicitly enables Spark extraction; replacing
--candidate with --real explicitly enables budgeted Muse Code authoring for a
conflict-free confirmed spec. Both share the canonical daily $5 ledger and refuse
unknown prior usage. Real keys remain only in the trusted parent/gateway; the
Muse child gets a minimal environment and a dummy stdin credential. No live calls
were made today. These new live paths have only fake-provider/offline validation.

See SPEC_EVAL.md for the preregistered eight-document evaluation and exact command.
Local spec_runs/ and spec_eval/results/ are ignored by Git. Demo artifacts under
demo/spec-recorded/ contain only synthetic requirements and fake response evidence.
