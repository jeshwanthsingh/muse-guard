# Video plan: 3 minutes, real footage only

Every shot uses footage that already exists in the repo or on the live site. Nothing is simulated or staged. Shots marked **[YOUR RECORDING]** need your own screen capture, which is not yet made.

Live page: https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/
Static demo (run locally with the README quickstart, served at http://127.0.0.1:8000): `output/submission-site/index.html`

| Time | On screen | Exact file or URL | Caption |
|---|---|---|---|
| 0:00–0:12 | Live page top: the H1 and the "Live: requirements check only" banner. | https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/ | Paste plain-English rules. Find conflicts before any code exists. |
| 0:12–0:24 | Click "Sample: Refund notes (recorded extraction)". The status line says no model call was made. | Same page, sample button | A saved real extraction, labeled as recorded. No model call. |
| 0:24–0:40 | Confirm rules 1–3 one at a time. The Check button stays disabled, and the note beside it lists the rules still waiting. | Same page, Step 2 | Check stays off until every rule is decided. |
| 0:40–1:00 | Step 3: "1 conflict (A vs B), 1 input affected" with the decision-preview table. | Same page, Step 3 | Exhaustive search finds the input where the rules disagree. |
| 1:00–1:12 | Pick "B wins", click "Approve choices", then download the evidence JSON. | Same page, Steps 4–5 | Approved rules and an evidence file you can download. |
| 1:12–1:26 | **[YOUR RECORDING]** Terminal: `muse-guard returns --real --out returns_runs/real-2026-10-29-b`, the prompt where the developer chooses B, and the final CHECKED / PASS line. | Your screen capture; the run folder is `returns_runs/real-2026-10-29-b/` | Real run: one developer choice, one Muse Code edit, one independent check. |
| 1:26–1:40 | Main recorded returns run: PASS, 4/4 policy cases, 7/7 existing regressions, model cost $0.14362. | https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/recorded/returns-run/index.html (local source: `returns_runs/real-2026-10-29-b/index.html`) | The recorded run, with its checks and cost, on the live site. |
| 1:40–1:55 | Section 3 "Rule B wins" with "interactive human CLI choice"; then section 4 diff of `refund_policy.py`. | Same page, sections 3–4 | The developer chose B. Muse changed the policy file. |
| 1:55–2:08 | Section 4 line "Agent edited original tests: yes (descriptive)". | Same page, under the section 4 diff | Muse also added one test. The record says so. |
| 2:08–2:22 | Static demo study card: 0 / 0 / 0; 39/40 → 40/40; +2% cost · +9% steps. | http://127.0.0.1:8000/ (`output/submission-site/index.html`) | Measured holdout study: 160 runs. The recovery gap is not a proven advantage. |
| 2:22–2:34 | Planted-cheat recorded page: "UNAUTHORIZED TEST CHANGE", labeled as a planted fixture. | https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/recorded/recorded-runs/runs/planted-edited-test.html (static copy: `output/submission-site/runs/planted-edited-test.html`) | Planted fixture: an edited test cannot turn a failing implementation into a pass. |
| 2:34–2:45 | Evidence download on the returns run page: "Download evidence record". | Same returns run URL, bottom of page | The full run record is downloadable. |
| 2:45–3:00 | Live page "What this does NOT check" box. | https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/ (scroll to the box) | Checked over declared inputs. It is not a proof. |

## Notes

- Captions are one line each and use the same wording as the pages.
- Shot 6 uses the real run folder. The terminal capture in shot 6 must come from your own run; if it is not recorded, drop that shot and keep the viewer page.
- The planted-cheat page is a labeled fixture, not Muse behavior. Keep the caption that says so.
- Do not show the stopped run A record, or any file outside the repo.
