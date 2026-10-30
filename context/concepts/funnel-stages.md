---
id: funnel-stages
title: Funnel stages
owner_team: Sales
status: canonical
last_reviewed: 2026-10-30
related: [mql, mrr, cross-cutting-rules]
---

# Funnel stages

## Definition

A deal moves forward through four open stages: qualification, discovery, proposal and negotiation. It ends in one of two closed stages, closed_won or closed_lost. Entering a stage is the event that counts, and the CRM records its date.

## Rules

- Stage order is qualification, discovery, proposal, negotiation, then closed_won or closed_lost. The order is available as [[gold.funnel_stage_monthly.stage_order]]. Stages are never skipped.
- A deal enters each stage at most once, on the date in [[silver.deal_stage_history.entered_at]]. A deal's current stage is [[silver.deal.stage]].
- Qualification: entered when an SDR hands over a lead that [[concept:mql]] flagged and the account owner opens the deal. Left when budget, need and decision maker are confirmed.
- Discovery: entered after the first discovery call is held. Left when the customer's problems are written down and the product is confirmed to fit.
- Proposal: entered when a written proposal is sent. Left when the customer asks to negotiate or declines.
- Negotiation: entered when price and terms are under discussion. Left when the customer signs or declines.
- closed_won: the customer signed. A subscription starts within two weeks, see [[concept:mrr]]. closed_lost: the customer declined, or the deal had no activity for 90 days.
- Funnel volume is the number of deals that entered a stage in a month: [[gold.funnel_stage_monthly.deals_entered]]. Their yearly contract value is [[gold.funnel_stage_monthly.amount_usd_entered]], from [[silver.deal.amount_usd]].
- Stage-to-stage conversion follows cohorts, not months. A cohort is the deals that entered qualification in one month, [[gold.funnel_conversion_monthly.cohort_month]]. Conversion into a stage is the deals of the cohort that ever entered it, for example [[gold.funnel_conversion_monthly.reached_discovery]], divided by [[gold.funnel_conversion_monthly.deals_qualified]] or by the previous stage.
- Win rate is closed_won divided by closed_won plus closed_lost, from [[gold.funnel_conversion_monthly.closed_won]] and [[gold.funnel_conversion_monthly.closed_lost]]. Open deals ([[gold.funnel_conversion_monthly.still_open]]) are left out of it, never counted as lost.
- Time in stage is how long a deal stayed in an open stage, grouped by the month it left: [[gold.funnel_time_in_stage_monthly.median_days_in_stage]] (the median) and [[gold.funnel_time_in_stage_monthly.avg_days_in_stage]]. Leaving means entering the next stage, closed_won and closed_lost included. Prefer the median, a few very slow deals pull the average up.
- Deals without a company ([[silver.deal.has_company]]) are in the funnel like any other deal, and are listed for cleanup in [[concept:cross-cutting-rules]].

## Gotchas

- For a small share of deals the CRM stores stage dates out of order. Monthly entry counts can be slightly off for those deals.
- A stage with no entries in a month has no row in [[gold.funnel_stage_monthly.month_stage_key]]. Treat a missing row as zero.
- Do not divide the entries of one month by the entries of the previous month: those are different deals. Use the cohort table.
- Recent cohorts are immature. A cohort from the last two or three months still has many open deals, so its conversion and win rate look low and will rise. Compare only cohorts old enough to have closed.
- A deal can close lost without passing every open stage, so a stage count can be lower than the closed count of the same cohort.
- Time in stage only covers deals that already left the stage. A deal stuck in a stage for months is not in the figure yet, so a good median can hide a growing backlog. Compare it with the open deals of the cohort.
- Exits with dates out of order are counted in [[gold.funnel_time_in_stage_monthly.out_of_order_exits]] and left out of the day figures.
- No loss reason exists in the CRM data, so why a deal was lost cannot be answered from gold.
- Counting deals that entered a stage is not the same as counting deals currently in it.
- closed_won is a sales event, not revenue. Revenue starts with the subscription, see [[concept:mrr]].
- The funnel here starts at qualification. Earlier steps, from form submission to qualified lead, are in [[concept:mql]].

## Team differences

- SDRs say "qualified" when a lead is flagged and accepted. Sales says "qualified" only once the deal is in discovery, after budget, need and decision maker are confirmed. **The stage definitions in this document are canonical**, so a deal is "qualified" for the funnel when it leaves qualification.

## Examples

A deal created on January 5 enters qualification on January 5, discovery on January 20 and proposal on February 3, then stops. January funnel volume counts it once in qualification and once in discovery, and February counts it once in proposal. It is still open, so it has no closed date.
