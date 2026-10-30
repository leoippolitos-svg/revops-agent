---
name: add-connector
description: Registers a new connection to an external system in connectors/registry.yaml with the least privilege that works. Use when the user mentions a new tool, API, "integration", "connect to", "webhook" or "service account", or when new code would talk to a system that is not in the registry.
---

# Add a connector

Standard: `docs/standards/connectors.md`. If it is not in the registry, it does not exist.

## Steps

1. Name the consumer (pipeline, agent, MCP server, app, automation) and the exact data or action it needs.
2. Choose the status: `live` only if it works in this repo today, `simulated` if fake data stands in, `documented` if it is only described.
3. Choose the smallest access. `read` unless an effect is required. List exact `scopes`, never "full access".
4. Describe `auth` as a method and the name of the variable, never a value. The secret goes in `.env`, which this agent never reads. Add the variable name, empty, to `.env.example`; if the tool denies that file, ask the owner to add it.
5. Add the entry to `connectors/registry.yaml` with `id`, `system`, `status`, `access`, `scopes`, `auth`, `consumers` and `owner`.
6. For `read-write`, write an ADR in `docs/adr/` that says why read is not enough and how the write is limited. Link it in the entry's `note`.
7. Open an `infra` PR with `open-pr`.

## Example

A Slack alert channel: `access: read-write`, `scopes: ["post to one channel"]`, `status: documented` with a note that alerts are written to `observability/` in the meantime, and an ADR for the write.

## Troubleshooting

- **The consumer needs more scopes later**: change the entry in a new PR. Never widen silently.
- **A key was pasted in chat or a file**: do not commit it. Tell the owner to rotate it.

## Never

- Put a credential, even a test one, in the registry.
- Give the RevOps agent a `read-write` connector.
