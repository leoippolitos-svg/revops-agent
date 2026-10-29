# Connectors

Every connection to an external system is registered in [`connectors/registry.yaml`](../../connectors/registry.yaml), live or simulated. If it is not in the registry, it does not exist.

## Fields

| Field | Meaning |
|---|---|
| `id` | Short name |
| `system` | What it connects to |
| `status` | `live` (works in this repo), `simulated` (fake data stands in), `documented` (described, not built) |
| `access` | `read` or `read-write` |
| `scopes` | Exact permissions requested |
| `auth` | How it authenticates, never the secret itself |
| `consumers` | Which pipelines, automations or agents use it |
| `owner` | Team responsible |

## Adding a connector

1. Open an `infra` PR adding the registry entry.
2. `read-write` access requires an ADR explaining why read is not enough.
3. Credentials go in `.env`, named in `.env.example`.

## Ways the gold layer is consumed

| Mode | Depends on | In this repo |
|---|---|---|
| Agent (natural language) | Context documents | `agent/` |
| MCP | Catalog + context documents | `mcp_server/` |
| BI / SQL | Good modeling | Direct DuckDB access |
| Destinations (reverse ETL) | Good modeling | `destinations/`, simulated |
