# Baseten go/no-go for the Nov 1 DEV run

Status as of 2026-10-29: **NO-GO.** No Baseten call has been made, and none is planned until the conditions below are met.

## Why it is NO-GO

1. **No verified pre-call token counter.** `docs/BASETEN_EXPLORATION.md` requires a counter validated from official documentation for the shared endpoint. The official Model API overview page (`docs.baseten.co/inference/model-apis/overview`, fetched 2026-10-29) does not describe a token-counting endpoint or tokenizer. Without one, the pre-call cost reservation cannot be proven.
2. **The live executor is not reviewed.** `submission_tools/baseten_compare.py --execute` refuses by design. The offline plan is balanced: 40 entries, 10 DEV pairs, both backends, solvable and impossible tasks.
3. **The spend cap conflicts with the shared ledger.** `docs/BASETEN_EXPLORATION.md` says the grant is credit, not a relaxation of the shared $5 daily limit, and that this run competes with the pilot and spec evaluation for the same $5. A $40 cap would need its own ledger. None exists.
4. **The arm design differs from the request.** The preregistered doc compares backends with guarded recovery in both arms. The request for this run said "plain + guarded". Changing the arms is a design amendment, not an implementation detail.

## Cap arithmetic (conservative reservation)

| Quantity | Value |
|---|---|
| Reservation per attempt: 320,000 tokens × $4.25 / 1M output rate | $1.36 |
| Initial flows only (40 attempts) | $54.40 |
| Initial plus repairs (60 attempts) | $81.60 |
| Attempts that fit under a $40 cap at $1.36 each | 29 |

Under the conservative reservation, a $40 cap cannot admit the 40 initial flows. The doc's cost estimate of about $2.07 without caching depends on a verified counter that does not exist yet. The rates are the doc's own figures, from 2026-10-26; I did not recheck them today.

## Conditions to change to GO

All of these must be true before Nov 1:

- [ ] A pre-call token counter for `meta-models/muse-spark-open-1026` is documented by Baseten, tested with fake responses, and reviewed.
- [ ] The balanced executor is reviewed and tested with fake Baseten responses.
- [ ] The owner has decided the spend ledger. Either the $40 cap gets its own ledger, or the cap is replaced by the shared $5 limit.
- [ ] The owner has decided the arms: guarded only, as preregistered, or plain plus guarded, as an amendment.
- [ ] `docs/BASETEN_EXPLORATION.md` is amended for any change above, with failed and stopped attempts kept.

## Commands for Nov 1 (usable only after every condition above)

These commands run the offline plan and preflight. They make no inference call.

```sh
cd ~/Projects/muse-guard
git switch codex/submission
python3 submission_tools/check_protected.py
python3 submission_tools/baseten_compare.py --plan
set -a
. ./.env
set +a
python3 submission_tools/baseten_compare.py --preflight
```

Expected today: `--preflight` prints `status: refused` with the blocker and exits 2. A GO requires preflight to show the counter as validated. Do not run `--execute` until the GO checklist is complete.

## Two-hour go/no-go note (decide by T-2h before any run)

1. Check the daily ledger in `results/total.json`. `can_start` must be true, and the remaining allowance must cover the decided cap.
2. Run the preflight commands above. The counter must show validated, not blocked.
3. Confirm each box in the GO checklist, with the file or doc that shows it.
4. Write the decision into `docs/BASETEN_EXPLORATION.md` as GO or NO-GO, with the time.
5. If any box is unchecked, the decision is NO-GO. Record it and do not retry.

## Hard limits (unchanged from the exploration doc)

- Same 12 coding steps, 320,000 tokens and 300 seconds per attempt; 2,048 output tokens per request.
- Shared canonical ledger; no reset; $100 grant credits are not treated as zero-cost tokens.
- Maximum one repair per flow; no holdouts; no post-result changes to prompt, order, budget or labels.
