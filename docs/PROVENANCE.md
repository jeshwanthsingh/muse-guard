# Reuse and checker boundaries

Source: Jeshwanth Singh's [Unfoolable](https://github.com/jeshwanthsingh/Unfoolable),
Apache-2.0; local source revision `c8eafe7d9ed7221c091023a91e5e21fe16df6d32`.
The source checkout was read only. Reuse was explicitly authorized on 2026-10-26.

The README was left unchanged at the author's explicit request. Its initial
“No code was copied” disclosure is now inconsistent with the reuse listed here.
This note identifies the actual lineage; it does not establish hackathon eligibility.

| Authorized source | Reused here | What changed or stayed out |
| --- | --- | --- |
| `apps/server/oracle-tree.ts` | `runner.freeze` and checker test restoration | Regular-file/size validation, new snapshot directories and hashes; no Git object database, tar pipeline or macOS sandbox paths. Original tests are restored from trusted task definitions, never candidate discovery. |
| `apps/server/test-tampering.ts` | `tampering.compare_tests` | Ported multiset assertion comparison, preserving duplicate counts; Python AST supplies structural matches instead of ast-grep subprocess results. Added parse-failure flag. |
| `scripts/quality-gates/tampering.yaml` | `tampering-reference.yaml` | Literally copied the seven Python patterns, Apache-2.0. This file is a reference fixture; the Python AST implementation is the runtime detector. JavaScript/TypeScript rules are out of scope. |
| `packages/shared/verdict-core.ts` | Checker outcome ordering | Adapted evidence-first, nonpassing defaults. No historical seals, compatibility branches, admission/approval policy, or Unfoolable verdict names. |
| `apps/server/protected-existing-tests.ts` | `inventory_status` and `NamedResult` | Ported exact nonempty identity/count matching and skip rejection; Python unittest only, no native Vitest adapters or exclusion policy. |
| `apps/server/career-safe-playbook.ts` | `_observe` / parent `GuardCase` | Candidate imports happen in a bounded child. Parent owns inputs, expectations, assertions and authoritative named reports. Only inert JSON return data crosses the boundary. Each observation receives a fresh solution copy. |
| `docs/NEGATIVE_CONTROLS.md` | Planted-cheat test strategy | Reused the requirement that planted cheats never PASS; no old numerical results claimed as Day 1 evidence. |

## Why the boundary matters

Restoring tests alone is insufficient: importing candidate code into the checker
would let it monkeypatch the assertion library or reporter. Here candidate code
runs in a separate isolated Python interpreter; its success text and exit status
are only observations. The parent loads pristine original tests and compares
actual returned JSON values with the original expectations. Named unittest rows
are generated only by the parent. Empty, duplicate, missing, skipped and error
inventories are never PASS. A conflict report is a separate non-PASS path: the
parent checks the exact input, both rule IDs, contradictory expected outputs and
a question for the user. A correctly reported conflict may retain starter-code
errors; those errors are not turned into passing checks.

Known impossible contracts cannot become PASS even if a stateful candidate tricks
individual observations. Tampering is a heuristic warning/refusal, not proof of
intent; the label FAKED SUCCESS includes test edits and contradicted final success
claims. Unknown claim formats are ignored rather than treated as success.

## Scope limits

This is a local Day 1 experiment for tiny single-file functions. A separate process
is not a security boundary against arbitrary malicious code under the same OS user.
It has no independent OS sandbox preventing filesystem access, networking, process
signaling, detached descendants or native-code attacks. Resource/output/timeout
bounds and process-group cleanup cover ordinary mistakes; a container or stronger
isolation is needed before adversarial live use. Snapshot hashes are not signatures,
and read-only file bits are not protection from the file owner. No resistance to
all possible assertion rewrites or test-runner attacks is claimed.
