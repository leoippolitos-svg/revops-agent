---
id: metrics-onboarding
title: Onboarding metrics
kind: metrics
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [area-onboarding, closed-won-provisioning]
---

# Onboarding metrics

## Purpose

The official formula of every metric the Onboarding area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any Onboarding number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-onboarding]]. Customer Success owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Time to go-live | days from the kickoff milestone to the go_live milestone of a subscription | [[silver.onboarding_milestone.reached_at]] | not in gold yet |
| Stuck before go-live | subscriptions with a kickoff and no go_live after 60 days | [[silver.onboarding_milestone]] | not in gold yet |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.

## Internal benchmark

None yet.

## Interpretation notes

- A subscription that churns before go-live is an onboarding loss as much as a Customer Success one; report it in both, labelled.
