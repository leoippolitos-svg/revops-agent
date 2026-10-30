# ADR-0010: Lead routing may set one field, the owner

- Status: accepted
- Date: 2026-10-30

## Context
Routing a lead means changing who owns it in the CRM. That is a write to a source system, and the security standard says a write needs an ADR and a dry-run mode. Reading alone cannot do the job.

## Decision
The `lead-routing` automation may write one thing: the owner of a lead. Its connector, `crm-owner-assignment`, is registered as read-write, status `documented`, with the single scope "set the owner of a lead". Dry-run is the default and a flag turns the write on. In this repository the write goes to a file in `observability/logs/`, never to a real CRM. The routing rules are not in code: they are in the context document `lead-routing`.

## Alternatives considered
- **A person assigns every lead by hand**: safe, and slow, and the reason the rule exists.
- **The agent assigns leads**: rejected. The agent advises and never executes, see `docs/standards/security.md`. The automation is a script with a fixed rule, and the agent only explains it.
- **A broader CRM write scope**: rejected. One field is enough, and a token that can only set the owner cannot delete or merge anything.

## Consequences
The write is small, reversible (the previous owner is kept in the log) and visible. `tools/check_connectors.py` keeps the agent and the MCP server from ever consuming this connector. Going live would need a real token with that one scope, and a new decision.
