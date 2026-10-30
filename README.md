# muse-guard

muse-guard finds every conflicting action among the confirmed rules and declared inputs, then independently checks the fix against every input in the approved rule table.

Requirements can contradict each other even when each sentence sounds reasonable.
A coding agent may stop, guess which rule matters, or claim a fix that misses the real requirement.
muse-guard makes the clash explicit, lets the developer decide, and checks the result independently.

```text
Spec → Clash found → You decide → Muse Code repairs → Independent checks
```

Muse Spark proposes rules from English and explains clashes. A deterministic checker verifies conflicts over a small finite input space; the developer confirms the translation and chooses the winning rule. Muse Code writes and repairs code, then a separate checker runs visible and hidden checks. The submission command now connects spec review, a developer decision, approved v2, Muse Code implementation and independent recheck in one record and page.

| Meta tool | Role |
|---|---|
| Muse Code | Writes and repairs code |
| Muse Spark | Turns English requirements into proposed rules and explains clashes |
| Muse Spark Open via Baseten | Planned second agent backend; offline adapter only, live comparison pending |

## Try it live

Live page: https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/

Paste requirements, confirm each proposed rule, see clashes and what each choice changes, and download approved rules plus evidence. The page includes one sample from a saved real extraction, labeled "recorded extraction". Live extraction is limited to 5 per hour per visitor and to a $10 public budget. A result means "checked over declared inputs". It is not a proof.

The local test build runs with fake model responses and makes no Meta calls:

```sh
python3 -m pip install -r live_demo/requirements.txt
python3 -m uvicorn live_demo.local_dev:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765.

## Try it in 60 seconds

Requires Git and Python 3.11+; this demo needs no key and makes no model calls.

```sh
git clone --branch codex/submission https://github.com/jeshwanthsingh/muse-guard.git
cd muse-guard
python3 -m http.server 8000 --bind 127.0.0.1 --directory output/submission-site
```

Open **http://127.0.0.1:8000**. In the existing checkout, start in the repository folder. To rebuild the current demo, run `python3 submission_tools/export_demo.py --out /tmp/muse-judge-demo` (choose a new folder), then serve that folder instead.

Try the clearly labeled fake-response spec example locally:

```sh
PATH="$PWD/submission_tools/bin:$PATH" muse-guard spec demo/continuous/refund.md --fake-response demo/continuous/fake-response.json --accept-all --decide B --out spec_runs/quickstart
```

Open the printed `index.html` path. Without `--accept-all`, you review each translation yourself.

[Static recorded demo](output/submission-site/index.html) · [Continuous flow](docs/CONTINUOUS.md) · [Study plan](docs/STUDY.md)

## Results

**160 pre-registered holdout runs = 20 locked task pairs × 2 twins × 2 repeats × 2 modes**, not 160 independent problems. Each mode has **80 initial attempts + 40 repairs**. Both had **0 contradicted claims, 0 test edits, and 0 visible-pass/hidden-fail repairs**.

Explicit completion claims: plain **40 initial + 37 repair = 77**, guarded **37 initial + 40 repair = 77**. Contradictions were **0/77 completion-claiming attempts in each mode** (also 0/120 total coding attempts per mode); an exit code is not a completion claim.

Recovery after one developer decision: **plain 39/40, guarded 40/40**. This one-flow difference is **not a proven advantage**. In the plain refusal, old rule files still contradicted the decision; refusing was reasonable. Guarded mode keeps instructions synchronized. This was not dishonesty. Both modes completed 40/40 solvable runs. Observed guarded overhead was about **+2% cost and +9% coding steps**, including explanation calls in cost.

Spec extraction passed the strict rubric on **7/10 docs**: 6/8 in the original set (all 5 clashes found, 0 false), and 1/2 in the separately preregistered Claude-written, user-reviewed set. Doc1 recognized four clashes in its own representation but failed the frozen Boolean/field/action matching rubric; it remains a failure. [Explanation of the three extraction failures](docs/EXTRACTION_FAILURES.md).

Two earlier cohorts were excluded for harness stops—reminder-export policy, then a repository-root/accounting bug—with both costs retained. The completed cohort cost $15.43881375; total including exclusions was $15.76510530.

The zero-valued measures are a null result: this study provides no evidence that muse-guard makes Muse more honest. [Counts, denominators, overhead math and limitations](docs/MEASURED_RESULTS.md) · [Full study report](docs/STUDY_RESULTS_2026-10-27.md)

Try the static demo's separate rule playground: toggle rules or edit actions to see grouped conflicts and exactly which declared inputs change under A wins versus B wins. Recorded development examples and the labeled planted-cheat fixture remain separate from study results. The submission CLI (`PATH="$PWD/submission_tools/bin:$PATH"`) also shows this preview before a decision and in `muse-guard view <run>`.

## Limits

Small finite rule tables, a restricted condition language, 20 holdout pairs, and one Muse Code version (1.4.2 with Muse Spark 1.3). An exact quote does not prove that an English requirement was translated correctly: developer review remains essential. The candidate sandbox currently requires macOS. Hidden checks test the approved requirements; they are not a proof of correctness for arbitrary software.

Built during the Meta Global AI Developer Hackathon (Oct 26–Nov 4, 2026).
On Day 1, seven detection patterns were copied from my earlier Unfoolable project. They and copied diagnostic wording were replaced on Day 6; Unfoolable is now a design reference only for the current implementation. Earlier commits preserve that history.
[Provenance](docs/PROVENANCE.md) · [Dated contributions](docs/CONTRIBUTIONS.md)

## Related work

[Kiro requirements analysis](https://kiro.dev/docs/specs/analyze-requirements/) analyzes inconsistencies, ambiguities and gaps in requirements.
[ImpossibleBench](https://arxiv.org/abs/2510.20270) studies coding agents exploiting tests using impossible variants of coding tasks.
[Harbor](https://www.harborframework.com/) provides a framework for sandboxed agent evaluation and optimization.
Our narrower focus is exhaustive finite-domain checking followed by a developer decision → repair → independent recheck, with explicit coverage limits. Requirements analysis itself is not a novelty claim, and this is not a claim that those projects lack these capabilities.
