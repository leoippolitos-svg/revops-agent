# Agent

| Path | Contents |
|---|---|
| [`agent.py`](agent.py) | The loop: route, call the allowed tools within the budget, answer, log. Built and tested with a scripted model (ADR-0015). `python agent/agent.py --plan "question"` shows the route without calling a model; `--ask` uses the adapter and needs `ANTHROPIC_API_KEY` |
| [`model_client.py`](model_client.py) | The adapter for the Claude Messages API, standard library only (ADR-0016). Tested against a fake API; never called with a real key |
| `directives/` | `AGENT.md` (identity and protocol), `routing.md` (intents), `fallback.md` (edge cases) |
| `skills/` | Business skills the agent loads on demand |
| [`router.py`](router.py) | Intent classifier. Built: rules in plain Python, tools, tier and skill read from `directives/routing.md` (ADR-0014). Scored by `python evals/run_router.py` |
| [`rag/`](rag/retrieve.py) | Lexical retrieval over the context documents. Built: `retrieve(question, k)`, BM25 in plain Python (ADR-0007, ADR-0012). Record search is in `rag/record_search.py` |
| `tools/` | Contracts of `query_gold`, `search_context`, `get_catalog`, `search_records`. All four built: `query_gold` (ADR-0013), `search_context`, `get_catalog`, `search_records` |

Design follows Anthropic's context engineering guidance: a short system prompt, few non-overlapping tools, and context loaded just in time.
