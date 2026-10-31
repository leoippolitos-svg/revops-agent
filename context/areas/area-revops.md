---
id: area-revops
title: RevOps area
kind: area
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [metrics-revops, cross-cutting-rules]
---

# RevOps area

## Purpose

How the RevOps area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about RevOps, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-revops]] and CRM fields in [[doc:crm-map]]; neither is repeated here. RevOps owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Own the data, the definitions, the routing and the tooling every other team relies on, and this agent.

## People

RevOps people own no deals and are not in the owner table. RevOps approves every change to context documents, routing and automations.

## Objectives

- Trusted data: zero deals without a company, see [[doc:okrs]].
- Every number the agent states comes from a tool call and a canonical definition.

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Data-quality flags | [[gold.data_quality_snapshot]] | the weekly audit |
| Automations healthy | the run catalog | every job ran and wrote what it should |
| Agent cost per answer | the observability log | see the cost rules |

## CRM objects

All of them, and RevOps writes nothing by hand: writes happen only through automations under [[doc:writeback-rules]].

## Benchmarks

Forecast accuracy and data-quality benchmarks are in [[doc:benchmarks]].

## Frequent questions

- "Did the jobs run yesterday?" From the run catalog.
- "Why do Marketing and Sales show different MQL numbers?" Two flags, see [[concept:mql]].

## Anti-confusions

- A data-quality flag is not a filter: flagged records stay in the numbers, see [[concept:cross-cutting-rules]].
