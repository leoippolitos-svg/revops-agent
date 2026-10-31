---
id: metrics-product
title: Product usage metrics
kind: metrics
owner_team: Customer Success
status: draft
last_reviewed: 2026-10-31
related: [area-customer-success, area-onboarding]
---

# Product usage metrics

## Purpose

The official definitions of how customers use Fernway's product: active users, work orders completed, adoption stages. The agent reads it when a question is about usage or adoption. Today the lakehouse has **no product usage source**, so every metric here is "not in the data" and the agent says so instead of using a proxy such as health score. Customer Success owns it with RevOps and fills it when a usage source is added, in the same pull request as the new models.

## Metrics

| Metric | Intended definition | Source | Status |
|---|---|---|---|
| Active technicians | technicians who completed at least one work order in the last 28 days | product usage events | not in the data |
| Work orders completed | work orders closed in the period, per customer | product usage events | not in the data |
| Adoption stage | trial use, team use, company-wide use, by share of licensed technicians active | product usage events | not in the data |
| Health score | the score the Customer Success tool computes, see [[silver.health_score.score]] | Customer Success tool | in silver, not in gold yet |

## Window and grain

- Usage metrics will use a rolling 28-day window ending on the data date, by customer.
- The health score is a snapshot per company and date; use the latest score per company.

## Internal benchmark

None until a usage source exists.

## Interpretation notes

- Health score is not usage: it mixes signals the Customer Success tool chooses. Do not present it as product adoption.
