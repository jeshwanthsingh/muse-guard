# Submission draft

Draft text for the hackathon submission. Every number below appears in [MEASURED_RESULTS.md](MEASURED_RESULTS.md). Placeholders in square brackets must be filled with real results before submitting.

---

**Title:** muse-guard - Resolve the policy. Check the code.

**Tagline:** Turn conflicting requirements into an explicit decision, a checked implementation, and evidence you can inspect.

**Theme:** Build for Your World

---

## Description

- **What it does.** muse-guard turns plain-English rules into a finite rules table. Each rule quotes its source sentence, and the developer confirms it. An exhaustive search then lists every declared input where confirmed rules demand different actions, before any code is written. The developer chooses the winner, and a coding agent implements the approved rules.
- **Independent recheck.** An independent checker runs visible and hidden tests against the approved rules. The result is a downloadable evidence record.
- **Measured holdout study.** 160 runs in the preregistered study: 20 locked task pairs × 2 twins × 2 repeats × 2 modes. These are repeated runs, not 160 independent problems.
- **Recovery after one decision.** Plain Muse 39/40 (97.5%); guarded recovery 40/40 (100%). The one-flow difference is not a proven advantage.
- **Honesty measures.** 0/77 contradicted claims among claiming attempts, and 0/120 contradicted claims among all coding attempts, in both modes. 0/120 original tests edited, and 0/40 visible-pass / hidden-fail repairs, in both modes. These zero measures are a null result: the study provides no evidence that muse-guard makes Muse more honest.
- **Cost and steps.** Observed guarded overhead: +1.64% cost (about +2%) and +9.37% coding steps (about +9%), for this sample only.
- **Spec extraction, strict.** 7/10 documents across two separately preregistered sets (6/8 original; 1/2 separately registered). All 5 ground-truth clashes in the original eight were found, with 0 missed and 0 false. One document failed on representation matching, and that failure is retained.
- **Scope.** Small finite rule tables; 20 holdout pairs; one Muse Code version (1.4.2, Muse Spark 1.3). Results do not establish correctness for arbitrary software, omitted requirements or undeclared inputs. Extraction accuracy claims require developer review.
- **Try it live.** https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/ — requirements check only. Code is not written or run on the live page. Recorded runs are linked from it.
- **Source.** https://github.com/jeshwanthsingh/muse-guard

## Real-world check

- [outside-user result: fill after the session. Rules fit the supported format: __; finished without help: __; clash understood: __. Source: session recording in docs/USER_SESSION_KIT.md, with consent recorded.]
- [real returns-run result: fill after the owner's run. Outcome, cost and evidence path: __. Not run by the builder.]

## Built during the event

muse-guard was built during the Meta Global AI Developer Hackathon. The contribution log, dated by day, is in [CONTRIBUTIONS.md](CONTRIBUTIONS.md). Provenance, including earlier reused material and its later replacement, is in [PROVENANCE.md](PROVENANCE.md). Unfoolable is a design reference only.
