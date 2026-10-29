---
id: active-customer
title: Active customer
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-29
related: [mrr, funnel-stages, cross-cutting-rules]
---

# Active customer

## Definition

An active customer is a company with at least one subscription in force and already paid at least once on the date in question. The company is what counts, not the subscription. Billing, not the CRM, is the source of truth.

## Rules

- Included: companies with a subscription that has started and not ended by the date, using [[silver.subscription.started_at]] and [[silver.subscription.ended_at]], and with a payment received on or before the date, using [[silver.payment.paid_at]].
- Excluded: subscriptions that have ended, subscriptions not yet paid, companies that only have a won deal and no subscription yet, and internal or test accounts (see [[concept:cross-cutting-rules]]).
- Counted per company: a company with two subscriptions is one customer. The company count is [[gold.active_customer_monthly.active_customers]] and the subscription count is [[gold.active_customer_monthly.active_subscriptions]].

## Gotchas

- A deal in stage closed_won ([[silver.deal.stage]]) is not a customer yet. The customer exists when the subscription starts and has been paid, see [[concept:funnel-stages]].
- A subscription whose deal is missing from the CRM still counts, because billing is the source of truth ([[silver.subscription.has_matching_deal]]).
- A company flagged as a possible duplicate ([[silver.company.is_possible_duplicate]]) can appear as two customers. Report it, do not remove it.
- Customers are counted at the end of each month. The last month is still in progress and uses the newest day of data.
- Not modeled yet, because Fernway's data has none: trials and payment grace periods. Add them here, and to the models, when they appear.
- Active customers and [[concept:mrr]] differ on purpose: MRR counts a subscription from the day it starts, even before its first payment.

## Team differences

- Sales says "customer" from the moment a deal is closed won, before the first payment.
- Customer Success uses this document's definition. **This one is canonical.**

## Examples

A company starts subscription A in March and pays its first invoice in April. It is not an active customer at the end of March, and it is one at the end of April. If it buys a second subscription in May, it is still one customer, with two active subscriptions.
