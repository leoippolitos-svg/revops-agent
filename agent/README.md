# Agent

| Path | Contents |
|---|---|
| `directives/` | `AGENT.md` (identity and protocol), `routing.md` (intents), `fallback.md` (edge cases) |
| `skills/` | Business skills the agent loads on demand |
| `router.py` | Intent classifier (planned, rules in `directives/routing.md`) |
| `rag/` | Chunking, transactional reingest and retrieval (planned, see ADR-0007) |
| `tools/` | Contracts of `query_gold`, `search_context`, `get_catalog`, `search_records` |

Design follows Anthropic's context engineering guidance: a short system prompt, few non-overlapping tools, and context loaded just in time.
