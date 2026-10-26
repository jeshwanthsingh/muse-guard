# Current provenance — Day 6 correction, 2026-10-26

The original blanket README claim was inaccurate once Day1 reuse occurred. This
correction supersedes that claim; the historical contribution entries and source
record below are retained rather than rewritten.

- **Copied on Day1:** seven Python ast-grep pattern definitions in
  `docs/tampering-reference.yaml`, and detector diagnostic wording from
  `apps/server/test-tampering.ts`. The first Python detector explicitly followed
  that file's multiset-comparison design.
- **Replaced on Day6:** deleted the entire copied reference file; wrote a fresh
  active `muse_guard/detection_policy.json` and scope-aware AST detector. Test
  ownership and occurrence ordinals now detect predicates moved between tests,
  repeated assertions, bare/aliased skips and constant-success checks. Wording
  and structure are new. The small legacy inventory helper was also rewritten
  as a remaining-identities traversal instead of retaining its port description.
- **Current relationship:** Unfoolable is a design reference only. Snapshot
  validation, independent child observations and exact test inventory principles
  informed the design; the audit found no other project-specific copied source
  blocks under the checks described below. These are bounded audit findings,
  not a mathematical proof of independent authorship.
- **History and demo:** earlier Git commits intentionally retain the copied
  material and old disclosures. The current demo must use the Day6 implementation,
  not the removed fixture or an old checkout. Historical experiment records are
  retained as evidence and are not rescored or presented as new event work.

## Whole-repository comparison

Compared every nonignored regular file in muse-guard against the local reference
checkout at `c8eafe7d9ed7221c091023a91e5e21fe16df6d32`, including the tracked/working
reference corpus. Methods: identical file hashes, five consecutive nonblank lines
with normalized whitespace, Python string-literal matching (20+ characters), and
manual review of the declared Day1 lineage and shorter detector diagnostics.
The audit records coverage and fingerprints without republishing removed patterns.

The actual copied fixture and detector wording are replaced. Other matches were:
standard Apache-2.0 license text, two empty package-marker files, the macOS sandbox
executable path, HTTP headers/MIME values, generic accessible span markup, a Markdown
table separator and standard Git test options. Those standard/empty fragments are
retained; their equality alone is not evidence that project code was copied.
No license text is rewritten. Ignored secrets, generated raw sessions and Git object
history are excluded from the source scan; historical commits are disclosed above.
See `results/DAY6_PROVENANCE_AUDIT.json` for the before/after audit inventory.

## Historical Day1 record (retained; current status is above)

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
intent; historical Day 1 labels are retained in saved records. New executions separate
UNAUTHORIZED TEST CHANGE from CLAIM CONTRADICTED; only an explicit completion
claim plus contrary independent evidence gets the latter label. Unknown claim formats are ignored rather than treated as success.

## Scope limits

Day 2 adds recovery and new secret-read restrictions. The candidate profile denies
networking, outside writes, user-home reads, common secret paths and other temporary
authoring locations; approved public runtime data is provided inside its observation
folder. New isolation/rules/recovery code was written in muse-guard, with no additional
Unfoolable copying. Parent-side approval is a trusted local boundary; hashes do not
attest an external human identity. Snapshot hashes are not signatures. Broader
production hardening and a Linux confinement backend remain future work.
