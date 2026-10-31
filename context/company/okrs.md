---
id: okrs
title: Objectives and key results
kind: okrs
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [company, mrr, funnel-stages, mql]
---

# Objectives and key results

## Purpose

The goals of the current cycle, so the agent can put a number next to its target. The agent reads it when a question asks "are we on track", or when a metric it reports has a key result. It holds targets and their baselines, never the current value: the current value is always queried, because a number written here would go stale. Leadership sets the targets; RevOps owns the document and updates it at the start of each cycle or when a target changes.

## Cycle

Fiscal year 2026, from 2026-01-01 to 2026-12-31. Baselines are the full month of December 2025, the last full month before the cycle. Targets are fictional, set for this repository.

## Objectives and key results

| Objective | Key result | Metric | Baseline (2025-12) | Target | Deadline |
|---|---|---|---|---|---|
| Grow recurring revenue | Ending MRR | [[gold.mrr_monthly.ending_mrr_usd]] | $124,132 | $250,000 | 2026-12-31 |
| Grow recurring revenue | New MRR per month | [[gold.mrr_monthly.new_mrr_usd]] | $21,558 | $25,000 every month of Q4 | 2026-12-31 |
| Keep customers | Churned MRR as a share of starting MRR | [[gold.mrr_monthly.churned_mrr_usd]] over [[gold.mrr_monthly.starting_mrr_usd]] | 1.9% | below 2% every month | 2026-12-31 |
| Build a healthier funnel | Win rate of mature cohorts | [[concept:funnel-stages]] | see the funnel review | 40% or more | 2026-06-30 |
| Build a healthier funnel | Marketing qualified leads per month | [[gold.mql_monthly.marketing_mqls]] | queried at answer time | +20% on the 2025 monthly average | 2026-12-31 |
| Trust the data | Deals without a company | [[gold.data_quality_snapshot.deals_without_company]] | 4 | 0 | 2026-03-31 |

## Area, OKR and metric

| Area | Key results it moves |
|---|---|
| Marketing | Marketing qualified leads per month |
| SDR and Sales | Win rate, new MRR |
| Enterprise | New MRR, win rate |
| Onboarding | Churned MRR (a customer that never goes live is the likeliest to leave) |
| Customer Success | Churned MRR, ending MRR |
| RevOps | Deals without a company, and the accuracy of every number above |

## How the agent uses them

- Query the current value, then compare it with the target and say the gap in the metric's unit: "ending MRR is $125,099, half of the $250,000 target, with 11 months to go".
- Never call a key result on track or at risk from a partial month, see [[concept:cross-cutting-rules]].
- If a question names a target that is not here, say there is no recorded target instead of inventing one.
- Status is not stored here. It is computed at answer time, and the answer says the data date.
