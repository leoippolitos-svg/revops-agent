# Agent

| Path | Contents |
|---|---|
| `directives/` | `AGENT.md` (identity and protocol), `routing.md` (intents), `fallback.md` (edge cases) |
| `skills/` | Business skills the agent loads on demand |
| `router.py` | Intent classifier (Phase 3) |
| `rag/` | Chunking, transactional reingest and retrieval (Phase 3) |
| `tools/` | `query_gold`, `search_context`, `get_catalog`, `search_records` (Phase 3) |

Design follows Anthropic's context engineering guidance: a short system prompt, few non-overlapping tools, and context loaded just in time.
