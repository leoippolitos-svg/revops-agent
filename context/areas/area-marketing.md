---
id: area-marketing
title: Marketing area
kind: area
owner_team: Marketing
status: canonical
last_reviewed: 2026-10-31
related: [metrics-marketing, mql, okrs]
---

# Marketing area

## Purpose

How the Marketing area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about Marketing, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-marketing]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Marketing owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Create demand: bring companies that fit Fernway's customer profile into the funnel, and hand them to Sales with a flag both teams trust.

## People

Marketing has no deal owners, so nobody from Marketing is in [[silver.owner]]. Campaign owners are recorded outside the data.

## Objectives

- More marketing qualified leads every month, see [[doc:okrs]].
- Lower cost per marketing qualified lead without lowering the share that Sales accepts.

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Form submissions | [[gold.mql_monthly.form_submissions]] | every submission, flagged or not |
| Marketing qualified leads | [[gold.mql_monthly.marketing_mqls]] | Marketing's count, canonical for Marketing |
| Flags in conflict | [[gold.mql_monthly.conflicting_flags]] | where Marketing and Sales disagree |
| Cost per marketing qualified lead | not in gold yet | campaign budget in [[silver.campaign.budget_usd]]; needs a gold model |

## CRM objects

Campaigns ([[silver.campaign]]) with a channel in [[silver.campaign.channel]]: paid search, paid social, email, webinar, event and organic. Form submissions ([[silver.form_submission]]) link a contact to a campaign.

## Benchmarks

External benchmarks are in [[doc:benchmarks]]. Internal history is the monthly series in gold.

## Frequent questions

- "How many MQLs did we get last month?" Marketing's count, for a full month.
- "Which channel brings the most MQLs?" Needs submissions by campaign channel, which is not in gold yet; the agent says it is a data task.

## Anti-confusions

- An MQL for Marketing is not an MQL for Sales; both counts exist, see [[concept:mql]]. Never add them.
- A form submission is not a lead: one contact can submit many times.
