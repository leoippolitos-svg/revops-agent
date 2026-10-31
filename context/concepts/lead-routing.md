---
id: lead-routing
title: Lead routing
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [mql, funnel-stages, cross-cutting-rules]
---

# Lead routing

## Definition

Lead routing decides which owner receives a new marketing qualified lead. The segment of the lead's company picks the team, and the owner with the most room in that team gets the lead. The rule exists so that no owner is overloaded while another has an empty queue.

## Rules

- Only leads that [[concept:mql]] counts are routed: the submission carries Marketing's flag, [[silver.form_submission.marketing_mql_flag]].
- The segment of the company, [[silver.company.segment]], picks the team. Enterprise goes to the enterprise team. Small business and mid market go to the sales team. The team of an owner is [[gold.owner_workload.team]].
- If the company already has an owner ([[silver.company.owner_id]]) in the right team, the lead goes to that owner, so one account keeps one contact point. Capacity does not override this.
- Otherwise the lead goes to the owner of the right team with the fewest open deals, [[gold.owner_workload.open_deals]]. A tie goes to the lowest [[gold.owner_workload.owner_id]], so the same input always gives the same answer.
- Capacity is a limit on open deals per owner: 30 for the sales team and 8 for the enterprise team. An owner at the limit receives no new lead.
- When every owner of the team is at the limit, the lead is not assigned. It is listed for a person to decide, and the shortage is reported.
- A lead with no company, or a company with no segment, is not routed. It is listed for cleanup, see [[concept:cross-cutting-rules]].
- Qualification starts after routing: the owner opens the deal and the funnel begins, see [[concept:funnel-stages]].

## Gotchas

- Open deals come from the newest daily export. Leads routed on the same day see the same count, so a batch must add each assignment to the owner's count as it goes.
- [[gold.owner_workload.open_deals]] counts deals, not leads waiting to be worked. An owner with a full inbox of new leads can still look free.
- Teams other than sales and enterprise (sdr, customer_success, onboarding) never receive routed leads.
- The limits above are a policy, not a measurement. Change them here, never in code.
- Open question for the owner: the rule above lets account continuity override capacity, but the automation spec forbids assigning a lead to an owner at the limit. The automation lists such a lead for a person instead of choosing either. Say which text is canonical.

## Team differences

- Sales leaders want the lead to go to whoever closes best. Marketing wants the fastest handoff. **The rule above is canonical**: fewest open deals, with account continuity first. Closing history is not used, because the sample per owner is too small.

## Examples

A mid market company without an owner submits a form and is flagged. The sales team has five owners with 15, 19, 20, 22 and 26 open deals. The lead goes to the owner with 15. If the company already belonged to the owner with 26, the lead goes to that owner, because account continuity comes first.
