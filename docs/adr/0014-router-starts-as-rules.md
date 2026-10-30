# ADR-0014: The router starts as rules, not a model

- Status: accepted
- Date: 2026-10-30

## Context
ADR-0006 says a router picks the tools, the model tier and the skill for each question. The router runs before the model, on every question, so a model call there adds cost and delay to the cheapest questions, and it can answer differently on the same input.

## Decision
`agent/router.py` classifies with ordered rules in plain Python, and reads the tools, tier and skill from `agent/directives/routing.md`, which stays the only place they are written. Writing and off-topic requests are checked first, so "send the report" is refused before it counts as a report. A revenue question no rule recognizes is read as `metric_lookup`, the cheapest intent, and the reason says so. No new dependency. `evals/run_router.py` scores it on the tuning cases and on a held-out file written before the router existed.

## Alternatives considered
- **A model call per question**: handles odd wording, but costs on every question, is not repeatable and cannot be unit tested.
- **Asking the user which intent they mean**: safe, but slow for questions that are clear.

## Consequences
Free, repeatable and traceable to one rule. Unusual wording falls to the default, so the score on questions from other people is the number to watch. If it drops, the interface (`route(question)`) lets a model-based router replace this file, with these cases as its test.
