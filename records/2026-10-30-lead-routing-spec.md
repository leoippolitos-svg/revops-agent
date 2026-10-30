---
date: 2026-10-30
type: automation
pr: "#29"
author: Leonardo Ippolito
---

# Lead routing, specified

## What was done
Wrote `automations/lead-routing/SPEC.md` ("Status: specified, not built", checklist unticked). Created the context document `lead-routing`, the gold model `owner_workload` (open deals per owner, no names), ADR-0010, the registry entry `crm-owner-assignment`, five retrieval eval cases and two context A/B questions for the new document, and a dbt data test.

## Why
Routing was a name in `automations/README.md`. The rule (segment picks the team, account continuity first, then fewest open deals, capacity limits) was nowhere, and the automation needs it in `context/`, not in code. It also needs one gold table with workload, which did not exist.

## Result or decision
- The only write is the owner of a lead. That needs an ADR and a dry-run mode (ADR-0010). The connector is read-write, status `documented`, and the registry checker keeps the agent and the MCP server from consuming it.
- Account continuity beats capacity: a company that already has an owner in the right team keeps it. The limits (30 for sales, 8 for enterprise) are a policy in the context document, set from the fictional data, where sales owners hold 15 to 26 open deals.
- When all owners are full, the lead is listed for a person, never given to an overloaded owner.
- Not built, not run. Checked: dbt build passes on `owner_workload` (6 tests), the full suite and every repo guard pass.

## Rules and context changed
New `context/concepts/lead-routing.md`, added to `context/index.yaml`. The catalog was regenerated.

## Follow-ups
Spec for `closed-won-provisioning`. Build the routing script when the agent exists. The router eval cases have no routing intent yet; add one if the agent should answer routing questions.
