---
id: funnel-stages
title: Funnel stages
owner_team: Sales
status: canonical
last_reviewed: 2026-10-29
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
- Deals without a company ([[silver.deal.has_company]]) are in the funnel like any other deal, and are listed for cleanup in [[concept:cross-cutting-rules]].

## Gotchas

- For a small share of deals the CRM stores stage dates out of order. Monthly entry counts can be slightly off for those deals.
- A stage with no entries in a month has no row in [[gold.funnel_stage_monthly.month_stage_key]]. Treat a missing row as zero.
- Counting deals that entered a stage is not the same as counting deals currently in it.
- closed_won is a sales event, not revenue. Revenue starts with the subscription, see [[concept:mrr]].
- The funnel here starts at qualification. Earlier steps, from form submission to qualified lead, are in [[concept:mql]].

## Team differences

- SDRs say "qualified" when a lead is flagged and accepted. Sales says "qualified" only once the deal is in discovery, after budget, need and decision maker are confirmed. **The stage definitions in this document are canonical**, so a deal is "qualified" for the funnel when it leaves qualification.

## Examples

A deal created on January 5 enters qualification on January 5, discovery on January 20 and proposal on February 3, then stops. January funnel volume counts it once in qualification and once in discovery, and February counts it once in proposal. It is still open, so it has no closed date.
