---
id: deal-discount
title: Deal amount and discount
kind: rule
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [metrics-sales, writeback-rules]
---

# Deal amount and discount

## Purpose

How a deal's amount follows its list price and discount, and who approves a change, so the CRM amount always matches the proposal. The amount recalculation and the agent read it. It does not define bookings or MRR. Sales owns it with Finance.

## Rules

- A deal's net amount is the list amount times one minus the discount, rounded to the dollar: [[gold.deal_amount.amount_usd]] should equal it.
- A difference under 1 dollar is not a change.
- The amount is a sensitive field: every change is a proposal approved item by item by Finance, never written automatically (`writeback-rules`).
- A discount above 20 percent also needs the approval of the sales lead, and the proposal says so.
- Only open deals are recalculated; a closed deal's amount is history.

## Owner and approvers

Sales owns the discount policy; Finance approves every amount change.
