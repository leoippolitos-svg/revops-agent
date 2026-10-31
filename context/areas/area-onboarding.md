---
id: area-onboarding
title: Onboarding area
kind: area
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [metrics-onboarding, closed-won-provisioning]
---

# Onboarding area

## Purpose

How the Onboarding area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about Onboarding, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-onboarding]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Customer Success owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Take every new customer from kickoff to go-live, so the subscription turns into daily use.

## People

Three onboarding managers, team value `onboarding`.

## Objectives

- A short time from kickoff to go-live, and no customer stuck before go-live.

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Time to go-live | not in gold yet | from [[silver.onboarding_milestone]], kickoff to go_live |
| Customers past each milestone | not in gold yet | kickoff, configured, go_live |

## CRM objects

Onboarding milestones ([[silver.onboarding_milestone]]) per subscription: `kickoff`, `configured` and `go_live`, dated in [[silver.onboarding_milestone.reached_at]]. Provisioning requests the kickoff, see [[concept:closed-won-provisioning]].

## Benchmarks

See [[doc:benchmarks]].

## Frequent questions

- "How long does onboarding take?" Needs a gold model of milestones; until it exists the agent says it is a data task.

## Anti-confusions

- Kickoff is not go-live. A customer is "onboarded" only at go-live.
