---
date: 2026-10-30
type: app
pr: "#33"
author: Leonardo Ippolito
---

# search_context as an agent tool

## What was done
Built `agent/tools/search_context.py`, the tool wrapper over the retrieval in `agent/rag/retrieve.py`. It validates the input, calls `retrieve`, and adds a warning to every section from a draft or deprecated document. Added 19 tests in `tests/test_search_context.py` and updated the README status lines and the contract row.

## Why
The retrieval was built but nothing could call it the way the agent will: with input from a language model, which can be empty, huge or the wrong type. The contract says the tool reads `context/` only and flags documents that are not canonical, and the wrapper is where that is enforced.

## Result or decision
- Rejected before any search: an empty or non-string question, a question over 500 characters, and a `k` that is not a whole number from 1 to 5 (`True` included, since Python counts it as 1).
- A question that matches nothing returns an empty list, not an error, so the agent can say it found no definition.
- `retrieve.load_chunks` now refuses an index entry whose path leaves the context folder. Before, a `..` in `context/index.yaml` would have been opened. The index is committed and reviewed, so this is a guard against a mistake more than an attack.
- The cap of 5 sections is a policy: more than that fills the model's context without helping the answer.
- Not covered: no agent calls the tool yet, and the warning text is a rule for the answer, not something a test can check in a model's reply.

## Rules and context changed
No business rule changed. The `search_context` row in `agent/tools/README.md` now states the input limits and the warning.

## Follow-ups
`get_catalog` and `search_records`, then the agent loop.
