---
date: 2026-10-29
type: data
pr: "#5"
author: Leonardo Ippolito
---

# Generator: deals, stage history, form submissions and injected issues

## What was done
The generator now also writes `crm/deals`, `crm/deal_stage_history` and `marketing/form_submissions`, adds a `sales_mql_flag` column to `crm/contacts`, and injects four kinds of data-quality issues, recorded in an answer key at `data/raw/_issues.json`. The tests grew from 10 to 18. The owner-list simplification suggested in the previous review is applied.

## Why
The pipeline and the agent need a funnel to measure and defects to catch. The answer key lets a test tell a planned issue from a generator bug.

## Result or decision
- With seed 42: 309 companies (300 plus 9 duplicates), 222 deals, 744 stage history rows, 505 form submissions and 56 injected issues.
- Issues: duplicate companies (same company, new id, name in capitals), deals without a company, two middle stage dates swapped, and Sales and Marketing MQL flags that disagree.
- Issues are injected after the clean data exists, with their own random generator, so a clean row never changes because of an issue. The base entities use the same random sequence as before: checked against the previous generator, owners and campaigns are byte-identical and contacts differ only by the new column.
- Deals are fewer than first estimated (222, not 500 to 600) because only about 60% of companies have deals and most have one. Enough for Phase 1; the share is one constant.
- Stage names are what the CRM stores. What each stage means is left to the `funnel-stages` context document in Phase 2, so no `context/` change here.

## Rules and context changed
none

## Follow-ups
Billing and Customer Success files and the subscription without a deal (next PR), then `--days`.
