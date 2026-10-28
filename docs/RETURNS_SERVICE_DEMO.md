# Returns-service demo design — 2026-10-28

Design only. Build during the event in the next work stage; no service or paid calls are authorized by this document. Keep it outside the frozen evaluation. Goal: show a policy conflict and developer choice changing a small working HTTP service, followed by independent checks of the approved policy and existing service behavior.

## Small service

Python standard library, localhost only, in-memory return records; start with one server file, one refund-policy module and ordinary tests. No real payments, production data, account login or external integrations. A next action such as `refund_immediately` is a simulated service response, not money movement.

| Endpoint | Existing behavior to build first |
|---|---|
| `GET /health` | 200 JSON service status |
| `POST /returns` | Validate Boolean `eligible` / `fraud_hold` plus an integer `amount_cents`; create a return with an ID; 201 JSON |
| `GET /returns/{id}` | Return the stored request and next-action status; unknown ID returns 404 |
| `POST /returns/{id}/evaluate` | Call the policy module, persist one next action and return the updated record; reject malformed requests |

Baseline policy: eligible requests return `refund_immediately`; ineligible requests return `reject`. Baseline tests cover create/get/evaluate, invalid input and unknown IDs, plus policy cases. The fraud-hold field is stored but does not yet change policy. Build and demonstrate this baseline before asking Muse to change it.

## Recorded demonstration, about 90 seconds

1. Show the running baseline: create an eligible, fraud-held return with `amount_cents: 2500`; evaluate its real ID and show HTTP 200 with `next_action: refund_immediately`. Also show an ordinary non-held eligible return working. Capture actual requests/responses, never prewritten success output.
2. Submit English requirements: A “For every eligible request, refund immediately.” B “For every request on fraud hold, do not refund until manual review.” Otherwise reject. Developer reviews both translations and the fallback.
3. The deterministic checker enumerates the four declared Boolean cases. Group the overlap into **1 conflict (A vs B), 1 input affected**. Preview `eligible=true, fraud_hold=true`: A wins → `refund_immediately`; B wins → `manual_review`. Other three outcomes do not change between these two choices.
4. Pause for the developer's real choice. The planned screen recording chooses B, but do not silently simulate a human choice. Save the witness, decision and approved v2 artifacts.
5. Muse Code edits the service's refund-policy function and any necessary service integration, using ordinary conditional code that receives stored return data. Keep the service architecture and endpoints. Do not replace the service with a lookup-table demo. Record the actual diff and session message.
6. Independent recheck: issue actual HTTP create/evaluate/get requests to a separately launched candidate service for all four declared policy cases against the approved v2. Show the same fraud-held request now returning `manual_review`; eligible non-held still returns `refund_immediately`, ineligible non-held still rejects, and ineligible held goes to `manual_review`. Run the existing non-policy regression tests too.

## Checker, reference and evidence boundary

The checker owns approved requirements, expected cases and immutable service regression fixtures outside the agent folder. Keep a tiny table interpreter using the existing `actions` function as the **reference answer only**; it determines expected actions, never the candidate service's implementation. Candidate code runs in the existing Mac sandbox with no provider key/network; the checker talks to a loopback-only service via a narrowly scoped local channel. Prototype and test the least privilege loopback allowance before any model call; do not weaken the existing study sandbox or reuse frozen evaluation paths.

The overlap baseline test becomes obsolete when B wins. Preserve its v1 result and record its approved v2 replacement; edits to obsolete agent-side policy tests are descriptive, not recovery failure. Existing create/get/input-validation/404 tests remain unchanged, and all unaffected policy cases must still pass. The checker restores its own approved-v2 tests and verifies test inventories. A failed service launch is a harness error, never a policy pass.

Display this exact scope line: **“Policy behavior checked over these declared cases.”** List the four inputs next to it. HTTP regressions are additional finite checks; this is not exhaustive verification of persistence, concurrency, authentication, payment processing or an arbitrary web service. No honesty-improvement claim.

One evidence record contains baseline HTTP requests/responses, source and approved-rule hashes, reviewed translations, grouped witness and decision preview, developer choice, v2, model/session usage receipts, actual code diff, per-case HTTP observations, regression check names/results, cost and elapsed time. Screens should show the running service and real responses alongside the run viewer.

## Work estimate and build order

| Work stage | Estimate | Verification |
|---|---:|---|
| Baseline service + tests + real request recording | 60–90 min | Baseline HTTP smoke and existing regression suite pass |
| Service process adapter and least privilege loopback channel | 60–90 min | No home-secret reads or external network; checker reaches only the candidate endpoint |
| Connect reviewed decision/v2 to Muse service edit and independent recheck | 60–90 min | Fake-response end-to-end flow first; all four policy cases + unchanged regressions |
| One authorized real run, viewer evidence and video rehearsal | 45–75 min | Actual receipts, code diff and HTTP observations agree |

Total about **4–6 hours**, with the local-channel isolation adapter the main uncertainty. Avoid a database, frontend framework and payment integrations. Before a real run, reserve a conservative model allowance within the fresh daily $5 cap and stop on unknown usage; the old toy-study cost is not a service-run quote. If isolation takes longer, finish that check before any paid call or demo recording.
