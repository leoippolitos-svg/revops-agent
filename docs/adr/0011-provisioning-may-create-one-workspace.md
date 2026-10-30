# ADR-0011: Provisioning may create one workspace per signed deal

- Status: accepted
- Date: 2026-10-30

## Context
Provisioning a customer after a closed won deal creates something in the product. That is a write to an external system, which needs an ADR and a dry-run mode. Reading alone cannot do it.

## Decision
The `closed-won-provisioning` automation may create one customer workspace and request the onboarding kickoff, nothing else. Its connector, `product-provisioning`, is registered as read-write, status `documented`, with exactly that scope. Dry-run is the default and a flag turns the effect on. In this repository the effect is a line in `observability/logs/`, never a call to a real product. The deal identifier is the idempotency key, so a second run for the same deal creates nothing. The rules are in the context document `closed-won-provisioning`.

## Alternatives considered
- **A person creates every workspace**: safe, slow, and the delay is what customers feel first.
- **The agent provisions**: rejected. The agent advises and never executes, see `docs/standards/security.md`.
- **Provision when the first payment arrives**: cleaner for duplicates, but it delays onboarding by up to two weeks. Held cases cover the risk instead.

## Consequences
The write is small and one-per-deal. It cannot set a plan, change a price or delete a workspace, because the token would not allow it. `tools/check_connectors.py` keeps the agent and the MCP server from consuming this connector. Going live would need a real token with that one scope and a new decision.
