---
id: mrr
title: Monthly recurring revenue
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-29
related: [active-customer, funnel-stages, cross-cutting-rules]
---

# Monthly recurring revenue

## Definition

Monthly recurring revenue (MRR) is the monthly value of every subscription in force on a given day. A subscription's MRR is a twelfth of its yearly contract value. Month to month, MRR moves with new subscriptions and with churn.

## Rules

- Included: subscriptions that have started and not ended by the day, using [[silver.subscription.started_at]] and [[silver.subscription.ended_at]], at the value in [[silver.subscription.mrr_usd]]. The total at the end of a month is [[gold.mrr_monthly.ending_mrr_usd]].
- New MRR is the value of subscriptions that started in the month: [[gold.mrr_monthly.new_mrr_usd]].
- Churned MRR is the value of subscriptions that ended in the month: [[gold.mrr_monthly.churned_mrr_usd]].
- The months connect: starting MRR ([[gold.mrr_monthly.starting_mrr_usd]]) plus new MRR minus churned MRR equals ending MRR.
- A payment is not required. A subscription counts from its start day, paid or not.
- Amounts are in US dollars and dates are calendar dates, see [[concept:cross-cutting-rules]]. Internal and test accounts are excluded.
- There is no expansion or contraction yet: a subscription keeps the same MRR for its whole life, because Fernway's data has no plan changes.

## Gotchas

- The last month is still in progress and stops at the newest day of data. Do not compare it with a full month.
- A subscription that starts and ends in the same month appears in both new and churned MRR, and not in ending MRR.
- A subscription whose deal is missing from the CRM still counts ([[silver.subscription.has_matching_deal]]): billing is the source of truth.
- Deal value is not MRR. The yearly value of a won deal ([[silver.deal.amount_usd]]) only becomes MRR when its subscription starts.

## Team differences

Sales reports bookings: the yearly value of deals closed won, see [[concept:funnel-stages]]. RevOps and Finance report MRR from subscriptions. **MRR as defined here is canonical** for recurring revenue; bookings are a different number and should be named as such.

## Examples

A won deal of 12,000 a year becomes a subscription with MRR of 1,000. It starts on March 10 and never ends: March new MRR includes 1,000 and every ending MRR from March on includes it. If it ends on June 20 instead, June churned MRR includes 1,000 and June ending MRR does not.
