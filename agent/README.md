# Agent

| Path | Contents |
|---|---|
| `directives/` | `AGENT.md` (identity and protocol), `routing.md` (intents), `fallback.md` (edge cases) |
| `skills/` | Business skills the agent loads on demand |
| `router.py` | Intent classifier (planned, rules in `directives/routing.md`) |
| [`rag/`](rag/retrieve.py) | Lexical retrieval over the context documents. Built: `retrieve(question, k)`, BM25 in plain Python (ADR-0007, ADR-0012). Record search is in `rag/record_search.py` |
| `tools/` | Contracts of `query_gold`, `search_context`, `get_catalog`, `search_records`. All four built: `query_gold` (ADR-0013), `search_context`, `get_catalog`, `search_records` |

Design follows Anthropic's context engineering guidance: a short system prompt, few non-overlapping tools, and context loaded just in time.
