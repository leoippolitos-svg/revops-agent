# Agent tools

Four tools, all read-only (ADR-0006). A tool that can write does not belong here.

## Model tiers

| Tier | Model id |
|---|---|
| `fast` | `claude-haiku-5-5` |
| `standard` | `claude-sonnet-5-5` |

## Contracts

| Tool | Input | Returns | Hard rules |
|---|---|---|---|
| `query_gold` | one SELECT statement | rows, at most 200 | Opens the lakehouse read-only. Only the `gold` schema may be read. One statement per call. Anything that is not a SELECT is rejected before it reaches the database. |
| `search_context` | question (at most 500 characters), k (default 3, from 1 to 5) | the k best context sections with document id, status and, for draft or deprecated documents, a warning | Searches `context/` only. Draft and deprecated documents are returned with their status so the answer can say so. |
| `get_catalog` | model name | the model and column descriptions | Reads the dbt `schema.yml` files, never the database. |
| `search_records` | question, k (default 3) | the k best past records from `records/` | Returns the record title, date and conclusion. |

## Budget

Lookups: up to 3 tool calls. Diagnoses: up to 8. When the budget runs out, answer with what was found and say what is missing (`agent/directives/AGENT.md`).

## Observability

Every question logs: intent, tier, tools called, token counts and latency, with no row data. The log is for debugging and cost, not for answers.

## Status

These are the rules, and two tools have code. The retrieval behind `search_context` is built (`agent/rag/retrieve.py`) and scored by `python evals/run_retrieval.py`. `query_gold` is built (`agent/tools/query_gold.py`, ADR-0013, proved by `tests/test_query_gold.py`). `search_context` is built (`agent/tools/search_context.py`, `tests/test_search_context.py`). `get_catalog` and `search_records` are not built. Code must pass `evals/` before it is trusted.
