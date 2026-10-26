# muse-guard

muse-guard catches requirement conflicts before your AI writes code, and proves every fix with checks the AI never sees.

Requirements can contradict each other even when each sentence sounds reasonable.
A coding agent may stop, guess which rule matters, or claim a fix that misses the real requirement.
muse-guard makes the clash explicit, lets the developer decide, and checks the result independently.

```text
Spec → Clash found → You decide → Muse Code repairs → Independent checks
```

Muse Spark proposes rules from English and explains clashes. A deterministic checker verifies conflicts over a small finite input space; the developer confirms the translation and chooses the winning rule. Muse Code writes and repairs code, then a separate checker runs visible and hidden checks. The new spec preflight and recorded recovery demo are separate entry points today.

| Meta tool | Role |
|---|---|
| Muse Code | Writes and repairs code |
| Muse Spark | Turns English requirements into proposed rules and explains clashes |
| Muse Spark Open via Baseten | Planned second agent backend; offline adapter only, live comparison pending |

## Try it in 60 seconds

Requires Git and Python 3.11+; this demo needs no key and makes no model calls.

```sh
git clone --branch codex/submission https://github.com/jeshwanthsingh/muse-guard.git
cd muse-guard
python3 -m http.server 8000 --bind 127.0.0.1 --directory output/submission-site
```

Open **http://127.0.0.1:8000**. The submission branch is currently local only; the clone command becomes available after its separately approved push. In the existing local checkout, start at `cd ~/Projects/muse-guard` instead.

Try the clearly labeled fake-response spec example locally:

```sh
PATH="$PWD/spec_guard/bin:$PATH" muse-guard spec spec_eval/docs/refunds.md --response spec_eval/fake/refunds.json --accept-all
```

Open the printed `index.html` path. Without `--accept-all`, you review each translation yourself.

[Static recorded demo](output/submission-site/index.html) · [Spec instructions](docs/SPEC.md) · [Study plan](docs/STUDY.md)

## Results

**Study pending.** Clean pilot: pending. Spec extraction evaluation: pending. Baseten comparison: pending.
The demo contains historical development recordings and a clearly labeled planted-cheat fixture; these are not completed-study results. No success rates are claimed.

## Limits

Small finite rule tables, a restricted condition language, and small samples. An exact quote does not prove that an English requirement was translated correctly: developer review remains essential. The candidate sandbox currently requires macOS. Hidden checks test the approved requirements; they are not a proof of correctness for arbitrary software.

Built during the Meta Global AI Developer Hackathon (Oct 26–Nov 4, 2026).
On Day 1, seven detection patterns were copied from my earlier Unfoolable project. They and copied diagnostic wording were replaced on Day 6; Unfoolable is now a design reference only for the current implementation. Earlier commits preserve that history.
[Provenance](docs/PROVENANCE.md) · [Dated contributions](docs/CONTRIBUTIONS.md)
