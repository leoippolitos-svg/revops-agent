---
date: 2026-10-29
type: data
pr: "#6"
author: Leonardo Ippolito
---

# Generator: billing and Customer Success

## What was done
Added `generator/billing_cs.py` and wired it into `generate.py`. A won deal becomes a subscription; each subscription produces monthly invoices, payments for the paid ones, onboarding milestones, monthly health scores and support tickets. The fifth planned data-quality issue, a subscription whose deal does not exist, is injected and recorded in the answer key. Tests grew from 18 to 29.

## Why
Gold needs recurring revenue (MRR, churn) and Customer Success signals next to the funnel, so the generator has to produce the right half of the Bowtie too.

## Result or decision
- With seed 42: 48 subscriptions, 663 invoices, 562 payments, 135 onboarding milestones, 615 health scores, 149 tickets and 58 injected issues in total. The CRM and marketing files are unchanged from the previous PR.
- Billing and Customer Success use their own random generator and are built from the clean deals before any issue is injected, so an issue in a deal (for example a missing company) never leaks into the subscription.
- One subscription per won deal. MRR is a twelfth of the deal amount, since the deal amount is a yearly contract value. About 15% of subscriptions churn.
- The simulated world has a last day (`WORLD_END`, 2026-12-31). Invoices not yet due on that day are `open`; older ones are `paid` or `overdue`. The tests check that nothing happens after it, which `--days` (next PR) builds on.
- The numbers above are source-system behaviour only. Definitions such as what counts as an active customer or how MRR is computed stay in the context documents of Phase 2, so no `context/` change here.

## Rules and context changed
none

## Follow-ups
`--days` and batches (next PR), then ingestion into bronze.
