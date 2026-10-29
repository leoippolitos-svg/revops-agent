---
id: active-customer
title: Active customer
owner_team: Customer Success
status: draft
last_reviewed: 2026-10-29
related: [mrr, cross-cutting-rules]
---

# Active customer

> Draft. Annotations will point to real models once the gold layer exists (Phase 2).

## Definition

An active customer is a company with at least one subscription that is paid and current on the date in question. Trials, internal accounts and companies whose only subscription is cancelled do not count.

## Rules

- Included: subscriptions with status paid [[gold.subscription_daily.status]] and at least one confirmed payment.
- Excluded: trials that never paid, test and internal accounts (see [[concept:cross-cutting-rules]]), subscriptions past their end date.
- Counted per company, not per subscription: a company with two subscriptions is one customer.

## Gotchas

- The CRM has a "customer" lifecycle stage that is set on closed won and never unset. It overcounts churned companies. Billing is the source of truth.
- A subscription paused for non-payment stays "active" in billing for 15 days of grace. During grace it still counts.

## Team differences

- Sales says "customer" from the moment a deal is closed won, before the first payment.
- Customer Success uses this document's definition. **This one is canonical.**

## Examples

On 2026-09-30 Fernway had 412 companies with a paid, current subscription, 9 of them internal or test accounts. Active customers: 403.
