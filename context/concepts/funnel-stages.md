---
id: funnel-stages
title: Funnel stages
owner_team: Sales
status: draft
last_reviewed: 2026-10-29
related: [mql]
---

# Funnel stages

## Definition

A deal moves forward through four open stages: qualification, discovery, proposal and negotiation. It ends in one of two closed stages, closed_won or closed_lost. Entering a stage is the event that counts, and the CRM records its date.

## Rules

- Stage order is qualification, discovery, proposal, negotiation, then closed_won or closed_lost. The order is available as [[gold.funnel_stage_monthly.stage_order]].
- A deal enters each stage at most once, on the date in [[silver.deal_stage_history.entered_at]]. A deal's current stage is [[silver.deal.stage]].
- Funnel volume is the number of deals that entered a stage in a month: [[gold.funnel_stage_monthly.deals_entered]]. Their yearly contract value is [[gold.funnel_stage_monthly.amount_usd_entered]].
- Deals without a company ([[silver.deal.has_company]]) are in the funnel like any other deal.
- Open question for the owner: the entry and exit criteria of each stage (what must be true to move from discovery to proposal, for example) are not written down yet. Fill them in here.

## Gotchas

- For a small share of deals the CRM stores stage dates out of order. Monthly entry counts can be slightly off for those deals.
- A stage with no entries in a month has no row in [[gold.funnel_stage_monthly.month_stage_key]]. Treat a missing row as zero.
- Counting deals entering a stage is not the same as counting deals currently in it.
- The funnel here starts at qualification. Earlier steps, from form submission to qualified lead, are in [[concept:mql]].

## Team differences

None known yet for the stage names. SDR and Sales may use "qualified" for different moments; confirm with the owner when the entry criteria are written.

## Examples

A deal created on January 5 enters qualification on January 5, discovery on January 20 and proposal on February 3, then stops. January funnel volume counts it once in qualification and once in discovery, and February counts it once in proposal.
