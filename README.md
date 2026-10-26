# muse-guard

When Meta's coding agent can't do a task honestly, it asks you
instead of faking it, and an independent checker proves it.

## What it is

Recovery for conflicting coding requirements: explain the conflict, let the developer decide, then let Muse Code repair.
An independent checker validates the witness and rechecks the approved implementation, including hidden inputs.

## Recovery flow

1. Muse Code returns a structured conflict report.
2. A deterministic checker verifies one input where two rules require different actions.
3. Muse Spark writes an advisory conflict card; the developer chooses a rule.
4. The checker creates approved requirements v2 and regenerates tests.
5. Muse Code repairs; separate sandboxed execution rechecks visible and hidden inputs.

Day 1 Muse reported all three impossible-task conflicts without faking success.
Recovery is the main experiment. Claim/tampering safety controls are explicitly
**planted fixtures**, kept separate from observed model behavior.

See [the Day 2 run](results/DAY2.md), [run instructions](docs/RUN.md), and the
[preregistered study design](docs/STUDY.md). No full study has run yet.

## One command

```sh
muse-guard run refund-impossible
muse-guard run refund-impossible --decide B
```

After a verified conflict, the first command pauses for your decision; the second
records a scripted choice. Both print an evidence summary and save the full record.
See [run instructions](docs/RUN.md) for environment setup and the offline quality gate.

## Status

Work in progress.

Built during the Meta Global AI Developer Hackathon
(Oct 26 - Nov 4, 2026).

## Prior work

Prior work by me, not part of this submission: Unfoolable
(https://github.com/jeshwanthsingh/Unfoolable). No code was
copied from it; it was used only as a design reference.
