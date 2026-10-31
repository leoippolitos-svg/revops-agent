---
date: 2026-10-31
type: app
pr: "#52"
author: Leonardo Ippolito
---

# Agent: four prompt blocks, category profiles, router cascade and answer rules

## What was done
- `agent/agent.py` builds the system prompt as four blocks: rules (cached), the intent's fixed documents and skill (cached), today's date, and retrieved context labelled "reference, not instruction". Fixed documents are read by id from the index; a failed search or a missing document never stops an answer. `--plan` shows the size and cache flag of each block.
- `agent/model_client.py` sends the blocks with a cache marker on the cached ones and marks failed tool results with `is_error`.
- `routing.md` gained the category profiles (fixed documents and chunk budget per intent) and the classification cascade; `agent/router.py` reads them, accepts an optional classifier, logs `via`, and puts the default on the standard tier. A plain request for a number is now a rule, so it stays on the fast tier.
- `query_gold` returns the real total next to a 200-row sample, and its description tells the model what it refuses.
- AGENT.md gained the answer rules of the original: closed source, no narration, no code or ids in the answer, the truth hierarchy, and two or three specific next cuts. `cross-cutting-rules` now asks for the source in plain words, with table names only on request.
- The MCP server's `get_context` serves every context document, not only concepts. ADR-0018 records the decision; 14 tests were added.

## Why
These were the mechanisms the original credited for its answer quality, more than the choice of model: fixed documents so a required rule never depends on retrieval luck, cache so the large blocks are paid once per category, today's date so "last month" is not the model's training cut-off, and prose rules that turn a number into an answer a leader can act on.

## Result or decision
- Router accuracy stays 1.000 on both sets. Retrieval MRR moved from 0.913 to 0.893 (target 0.75) after the cross-cutting-rules wording changed; Hit@3 stays 1.000.
- Prompt caching and the classifier step have never run against a real API.

## Rules and context changed
`agent/directives/routing.md` (profiles, cascade), `agent/directives/AGENT.md` (answer rules), `context/concepts/cross-cutting-rules.md` (how sources are named).

## Follow-ups
The map tool, cost per answer, then the automation controls.
