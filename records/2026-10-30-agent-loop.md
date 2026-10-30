---
date: 2026-10-30
type: app
pr: "#36"
author: Leonardo Ippolito
---

# The agent loop

## What was done
Built `agent/agent.py`: route the question, build the system prompt (protocol, fallbacks, the intent and the skill), let a model call the intent's tools within a budget, return the answer, and log one line. Added `--plan`, which shows the route, model and budget without calling a model. Added 22 tests with a scripted model, ADR-0015, and the README and observability updates.

## Why
Router, retrieval and the four tools existed, but nothing joined them, and the budget and the allowed tools were only sentences in a prompt.

## Result or decision
- The loop talks to a model through one method and imports no provider (ADR-0015), so no dependency was added and no key is needed.
- Held in code, whatever the model says: only the four read-only tools exist; a tool the intent does not allow is refused and still costs a call; 3 calls for the fast tier and 8 for the standard tier, after which the model is given no tools and must answer; a request to change, send or create is declined with no model call; a tool error goes back to the model as text and the loop continues.
- The log has intent, tier, tools, model calls, tokens and latency. A test checks that the question, an answer and a row value never reach it. Cost is not logged: there is no price table in the repo.
- Tests prove the loop and the guards. They do not prove the agent answers well, because the model in them is a script.
- Not built: the real model adapter (needs the provider package and a key, so its own ADR and the owner's decision), so the context A/B and skill-trigger evals still cannot run. Tier is taken from the router, so a question the router sends to `fast` cannot escalate.

## Rules and context changed
None. The README status lines now say what is built.

## Follow-ups
The real adapter, then the first scored run of the context A/B, the skill triggers and an answer-quality set. The MCP server and the micro-app.
