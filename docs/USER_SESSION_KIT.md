# User session kit

Kit for running short, solo sessions with outside developers on the live muse-guard page. Give the one-page guide to the developer ahead of time. The rest is for the person running the session.

---

## 1. One-page guide for the developer

**What muse-guard is.** muse-guard checks written requirements for conflicts before any code is written. You paste plain-English rules, confirm each rule the tool proposes, and it lists every input where two rules demand different actions. You then decide which rule wins, and it shows what each choice changes. Approved rules and an evidence file can be downloaded.

**What to bring.** Five to ten sentences of rules you wrote yourself, and which you are free to share. Write them the way a product or policy note would read, for example:

- Refunds are given when the order is eligible.
- Orders flagged for fraud are sent to manual review, always.
- If nothing else applies, the refund is rejected.

Use facts the tool can check. Each rule should depend on yes/no facts or on a small, fixed list of values, such as "eligible is true" or "order total is at least 100". Free-text fields, dates and unlisted values cannot be checked yet. Keep it to 2,000 characters. Do not include customer data, passwords or keys.

**Live page.** https://jeshwanthsingh--muse-guard-live-web.us-east.modal.run/

**No install needed.** Open the link in a browser. Paste your rules, then follow the five steps on the page. Your text is not logged or stored by the page. Check results against your own text.

---

## 2. Session script (30 minutes)

Run it solo: you sit beside them, but they drive the page.

| Time | What you say or do |
|---|---|
| 0–3 min | "This checks rules for conflicts before code exists. It does not write or run code, and it does not decide which rule should win. You do." Share the one-page guide. |
| 3–8 min | Ask them to paste their rules. Say nothing about whether the rules are good. |
| 8–15 min | They confirm or reject each rule against its source sentence. Ask: "Does this rule say what you meant?" Do not correct the rule for them. |
| 15–22 min | They read the clash table and the decision preview. Ask: "In your words, what happens when these two rules overlap?" |
| 22–27 min | They pick a winner for each clash and approve. Ask what they expect the approved rules to say before they look. |
| 27–30 min | They download the approved rules and evidence. Ask one open question: "What would you need before trusting this?" |

**What I do not help with.** I don't write or edit their rules, pick winners, explain what they "should" have meant, or click for them. If they are stuck, I say what the page says and wait. I can answer questions about the page, its limits and the evidence file.

**What I watch for.**
- Rules they reject because the proposal misquoted them, not because the rule is wrong.
- Long pauses on the same step, which usually means the wording is unclear.
- Any moment they expect the tool to check something it does not check (undeclared inputs, code, real systems).
- Any error message on the page, with the exact text.
- Whether they trust the output because the page says so, or because they checked the quotes.

---

## 3. Recording template

Fill one per session. Keep it short and factual.

- Session id (no name): ______
- Date and start/finish time: ______
- Rules they brought: how many sentences ______
- Did the rules fit the supported format? (yes / partly / no) and what did not fit: ______
- Rules they confirmed: ______ · rejected: ______ · not converted by the page: ______
- Rules corrected by them, and why (their words): ______
- Did they understand the clash? (yes / partly / no) Quote their explanation: ______
- Did they understand the decision preview? (yes / partly / no) Quote: ______
- Finished without help? (yes / no) If no, at which step: ______
- Time taken: ______ minutes
- Exact quotes on what was useful: ______
- Exact quotes on what was confusing: ______
- Bugs or page errors (exact text, step, browser): ______
- Consent (see section 4): ______

---

## 4. Consent line

Read it aloud and record the answer:

> "May I show your rules and quotes from this session in the muse-guard repository or in a video? You can say yes, or keep it private. Either answer is fine, and it won't change how we work together."

Record one: **shared in repo** / **shared in video** / **private (do not publish or quote)**. If private, do not put any of their rules or quotes in the repo, submission or video, even anonymized.

---

## 5. What I'll fix if it fails

Work through this list in order. Fix only what the session showed. Do not change recorded evidence.

1. **Page error or blank step.** Reproduce it on the live page with the same steps. Record the exact message. Fix the page, then tell the developer when it is fixed.
2. **Rules rejected for misquoting.** Check whether the proposed quote matches the source sentence exactly. If the page is wrong, fix the extraction display. If their wording is the problem, say so and leave the rule.
3. **Rules not converted.** Note which sentence and why. Do not add a rule for them.
4. **Confusing clash or preview wording.** Change the wording only, using their quotes as the test. Keep the meaning the same.
5. **Missing fallback warning unclear.** Make the blocked-approval message state exactly which inputs have no rule.
6. **Anything about the claim.** The page must keep "checked over declared inputs" and "not a proof". If the session showed someone reading more into it, fix the wording first.
7. **Anything else.** Log it in `docs/CONTRIBUTIONS.md` with the session id, and decide with the owner before changing the code.
