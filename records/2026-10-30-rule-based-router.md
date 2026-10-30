---
date: 2026-10-30
type: app
pr: "#35"
author: Leonardo Ippolito
---

# Rule-based router

## What was done
Built `agent/router.py`: ordered rules that give one intent per question, with the tools, tier and skill read from `routing.md`. Built `evals/run_router.py`, wrote `evals/router_heldout.yaml` (27 held-out cases) before the router, and extended `tools/check_evals.py` to validate that file and to fail if a held-out question is also a tuning question. Added ADR-0014 and 26 tests.

## Why
Every question starts at the router, and it was only a table. The target (accuracy 0.90) had never been measured, and the router eval cases had no request to assign, provision or change an owner.

## Result or decision
- Held-out file, scored on the first run with no tuning: 27 of 27. Tuning file (40 cases): 39 of 40 on the first run. The miss, "Why did a number change without any business change?", had no revenue word, so it was refused as off topic. Adding "business" to the revenue words fixed it. That is tuning on the tuning file, which is what that file is for.
- One rule I added on my own judgment, not from a case: "why did churn go up" is a trend question, not a funnel one, because there is no stage to blame. It is in the tests.
- `routing.md` changed. It said that when no intent fits the answer is `out_of_scope`, which would refuse "MQLs from webinars". It now says: a revenue question no rule recognizes is read as `metric_lookup` and the answer says so; only non-revenue or write requests are out of scope.
- Known weak spots: "don't" or "doesn't" anywhere sends a question to `data_quality`, and a question with no revenue word is refused even if it is about the business in other words.
- The held-out set has the same author as the router, so 27 of 27 shows the rules cover the way I phrase things, not how other people ask.

## Rules and context changed
`agent/directives/routing.md`: the ambiguity rule above. No context document changed.

## Follow-ups
Collect questions written by someone else and add them to the held-out file. Then the agent loop.
