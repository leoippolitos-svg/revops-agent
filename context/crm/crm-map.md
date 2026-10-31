---
id: crm-map
title: CRM map
kind: crm-map
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [entities, funnel-stages, data-map]
---

# CRM map

## Purpose

How Fernway's CRM is organised, object by object, and where each object lands in the lakehouse. The agent reads it before any question about deals, owners, companies or contacts, so it queries the right table and resolves stage and owner names instead of guessing. Business meaning stays in the concept documents; this map says where things are and how they are stored. RevOps owns it and updates it in the same pull request as any change to the CRM's pipelines, stages or fields.

## Pipelines and stages

One pipeline, new business. Stages in order, with the stage value stored in [[silver.deal.stage]] and the order in [[gold.funnel_stage_monthly.stage_order]]:

| Order | Stage value | Open or closed | Used by |
|---|---|---|---|
| 1 | `qualification` | open | SDR hands over, seller opens the deal |
| 2 | `discovery` | open | Sales and Enterprise |
| 3 | `proposal` | open | Sales and Enterprise |
| 4 | `negotiation` | open | Sales and Enterprise |
| 5 | `closed_won` | closed | provisioning starts |
| 5 | `closed_lost` | closed | no loss reason is recorded |

Stage entries are in [[silver.deal_stage_history.entered_at]], one row per deal and stage. Definitions of each stage: [[concept:funnel-stages]].

## Fields

| Object | Field | Where | Used by | Notes |
|---|---|---|---|---|
| Company | segment | [[silver.company.segment]] | routing, every area | `smb`, `mid_market`, `enterprise` |
| Company | industry, country, size | [[silver.company.industry]], [[silver.company.country]], [[silver.company.employee_count]] | Marketing, ICP | |
| Company | owner | [[silver.company.owner_id]] | routing continuity | the relationship owner |
| Company | duplicate flag | [[silver.company.is_possible_duplicate]] | RevOps | same name, ignoring case |
| Contact | job title, Sales flag | [[silver.contact.job_title]], [[silver.contact.sales_mql_flag]] | SDR, Marketing | |
| Deal | amount | [[silver.deal.amount_usd]] | Sales | yearly contract value, not MRR |
| Deal | stage, created, closed | [[silver.deal.stage]], [[silver.deal.created_at]], [[silver.deal.closed_at]] | Sales | current state only |
| Deal | owner | [[silver.deal.owner_id]] | Sales | the seller |
| Deal | has a company | [[silver.deal.has_company]] | RevOps | false means no association |

The only field an automation may write is the lead's owner, see [[doc:writeback-rules]].

## Owners

Owners are [[silver.owner]], with name and team. The agent never shows an owner id: it resolves the name through the map tool or [[silver.owner.full_name]], and the team through [[doc:entities]].

## Loss reasons

None. The CRM export has no loss reason, so "why did we lose" cannot be answered from data. The agent says so and offers what exists: the stage where lost deals stopped.

## Where it lands in gold

| Question | Gold table |
|---|---|
| Deals entering each stage per month | [[gold.funnel_stage_monthly]] |
| Conversion and win rate by cohort | [[gold.funnel_conversion_monthly]] |
| Time in stage | [[gold.funnel_time_in_stage_monthly]] |
| Open deals and value per owner now | [[gold.owner_workload]] |
| Data-quality flags | [[gold.data_quality_snapshot]] |

The agent reads gold only. A question no gold table answers is a data task, not a silver query.

## Model query

The query the agent starts from for "open deals by owner", with names resolved:

```sql
SELECT team, owner_id, open_deals, open_amount_usd
FROM gold.owner_workload
ORDER BY team, open_deals DESC
```

Owner names come from the map tool, not from a join to silver.

## Gotchas

- Stages are never skipped, but a few deals have stage dates out of order; their exits are counted apart in [[gold.funnel_time_in_stage_monthly.out_of_order_exits]].
- A missing stage in a month has no row: treat it as zero.
- Deals and companies keep their current state only; past states come from the stage history.
- The deal owner and the company owner can differ.
