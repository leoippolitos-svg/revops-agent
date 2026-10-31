---
id: area-sdr
title: SDR area
kind: area
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [metrics-sdr, mql, lead-routing]
---

# SDR area

## Purpose

How the SDR area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about SDR, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-sdr]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Sales owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Qualify marketing leads fast and hand qualified opportunities to the right seller.

## People

Five SDRs, team value `sdr` in [[silver.owner.team]]. SDRs never receive routed leads as owners, see [[concept:lead-routing]].

## Objectives

- Speed to lead: work every marketing qualified lead quickly.
- Hand over only leads that Sales accepts.

## KPIs

| KPI | Where | Notes |
|---|---|---|
| MQL to qualification | not in gold yet | needs submissions joined to deals |
| Speed to lead | not in the data | the time of first touch is not recorded |
| Sales-accepted leads | [[gold.mql_monthly.sales_mqls]] | the Sales flag, shown next to Marketing's |

## CRM objects

Contacts ([[silver.contact]]) carry the Sales flag [[silver.contact.sales_mql_flag]]. A qualified lead becomes a deal in the qualification stage.

## Benchmarks

See [[doc:benchmarks]].

## Frequent questions

- "How fast do we answer leads?" The data has no first-touch time, so gold cannot answer it; the agent says so.

## Anti-confusions

- SDRs say "qualified" when a lead is accepted; Sales says "qualified" after discovery. The funnel definition is canonical, see [[concept:funnel-stages]].
