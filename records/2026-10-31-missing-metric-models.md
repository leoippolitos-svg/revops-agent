---
date: 2026-10-31
type: data
pr: "#69"
author: Leonardo Ippolito
---

# Gold models for the metrics that were "not in gold yet"

## What was done
- Four gold models with catalog entries and dbt tests: `account_health` (latest score and band per company), `ticket_monthly` (opened and closed per month, category and priority), `campaign_channel_monthly` (budget, submissions and Marketing MQLs per month and channel, for cost per MQL) and `mql_to_deal_monthly` (MQLs that led to a deal for the same company within 30 days).
- The Marketing, SDR, Onboarding, Customer Success and product metrics documents, the area documents and the data map now point at gold; time to go-live uses the existing `onboarding_progress`.
- The `detect-risk` skill now works from gold: red band, onboarding stuck past 60 days and the ticket trend, each signal named; it says that product usage is not covered.
- A test checks the new models against silver totals.

## Why
Several metrics and one skill answered "this is a data task" because their data was only in silver; the agent reads gold only.

## Result or decision
- On the fictional data: 2 accounts in the red band, 50 tickets opened, cost per MQL computable for six channels, and MQL-to-deal for every month (the latest month is immature, as the metrics document says).
- One metric stays open on purpose: the enterprise win rate needs the segment in the cohort table.

## Rules and context changed
Metrics and area documents for Marketing, SDR, Onboarding, Customer Success and product; the data map.

## Follow-ups
The proposal and EBR apps with AI, and the security review pipeline.
