---
date: 2026-10-30
type: automation
pr: "#30"
author: Leonardo Ippolito
---

# Closed won provisioning, specified

## What was done
Wrote `automations/closed-won-provisioning/SPEC.md` ("Status: specified, not built", checklist unticked). Created the context document `closed-won-provisioning`, ADR-0011, the registry entry `product-provisioning`, five retrieval eval cases and two context A/B questions for the new document.

## Why
Provisioning was a name in `automations/README.md`. The rules (which deals are skipped or held, once per deal, where the plan comes from) were nowhere, and they belong in `context/`, not in code. The step also writes outside the repository, so it needs an ADR and a dry-run mode.

## Result or decision
- The only write is one workspace request per deal, behind ADR-0011. The connector is read-write, status `documented`, and the registry checker keeps the agent and the MCP server from consuming it.
- Skipped: a deal with no company, or one that already has a subscription. Held for a person: a company flagged as a possible duplicate. Nothing is dropped silently, each is listed with its reason.
- The plan and price come from billing, never from the automation. Provisioning does not make a company an active customer, which the context document and an A/B question state, because this is the easiest thing to get wrong.
- Checked in the fictional data: one closed won deal has no subscription yet, and subscriptions start 0 to 14 days after the win, which matches the two-week rule.
- Not built, not run. Every repo guard and the full test suite pass.

## Rules and context changed
New `context/concepts/closed-won-provisioning.md`, added to `context/index.yaml`. The catalog was regenerated and the A/B question count is now 18.

## Follow-ups
The specification of all three planned automations is now written. Building them waits for the agent. The router eval cases still have no routing or provisioning intent.
