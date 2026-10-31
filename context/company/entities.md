---
id: entities
title: Teams, people, segments and pipelines
kind: entities
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [company, lead-routing]
---

# Teams, people, segments and pipelines

## Purpose

Resolves vague references before the agent queries anything: "my team", "the enterprise people", "Dana's deals", "the pipeline". The agent reads it whenever a question names a person, a team, a segment or a pipeline. It holds who is who and which column groups them, never performance numbers. RevOps owns it and updates it the day someone joins, leaves or changes team.

## Teams

| Team value | Team | Owns | Receives routed leads |
|---|---|---|---|
| `sdr` | SDR | qualification of marketing leads | no |
| `sales` | Sales | SMB and mid-market deals | yes |
| `enterprise` | Enterprise | enterprise deals | yes |
| `onboarding` | Onboarding | implementation up to go-live | no |
| `customer_success` | Customer Success | retention and expansion | no |

The team of a person is [[silver.owner.team]]; the same value is in [[gold.owner_workload.team]]. Marketing and RevOps are teams too, but they own no deals, so they have no rows in the owner table.

## People and roles

- Every person who owns companies or deals is a row in [[gold.owner_directory]], with [[gold.owner_directory.owner_id]], [[gold.owner_directory.full_name]] and [[gold.owner_directory.team]].
- The agent answers with the full name, never the id: the map tool's `owners` key resolves one into the other.
- A deal's owner is [[silver.deal.owner_id]]; a company's owner is [[silver.company.owner_id]]. They can differ: the deal owner sells, the company owner keeps the relationship.
- Leaders by role: one head per team, recorded in the people directory outside the data. The agent does not guess who leads a team.

## Segments

`smb`, `mid_market` and `enterprise`, from [[silver.company.segment]], defined by employee count in [[doc:company]]. "Enterprise" can mean the segment or the team: the segment is a property of the company, the team is where the person sits. An enterprise company is sold by the enterprise team.

## Pipelines

Fernway has one deal pipeline, new business, with the stages in [[concept:funnel-stages]]. There is no renewal or expansion pipeline in the data: renewals and upsells are not tracked as deals yet. A question about "the renewal pipeline" has no data source, and the agent says so.

## Resolving vague references

- "My team": ask which team, unless the person asking is known to the agent; never assume Sales.
- "The sales team": the team value `sales`. If the question is about revenue from all sellers, it includes `enterprise` too, and the agent says which reading it used.
- "Dana's deals": the deals whose owner has the full name Dana Cole; if two people share a first name, ask.
- "Enterprise deals": deals of enterprise-segment companies. Deals without a company have no segment and are left out, with a note, see [[concept:cross-cutting-rules]].
- "The pipeline": open deals in the new business pipeline, stages qualification to negotiation.
