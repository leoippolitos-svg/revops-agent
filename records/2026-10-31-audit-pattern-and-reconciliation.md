---
date: 2026-10-31
type: automation
pr: "#58"
author: Leonardo Ippolito
---

# Audit pattern, deal and subscription reconciliation, duplicate companies queue

## What was done
- `docs/standards/audits.md`: the eleven-point skeleton of an audit (source of truth, explicit-id join with measured coverage, scope first, classification, three destinations, owner per class, actionable alert, proposal not correction, dry run then release, kill switch, never bulk), its traps, a spec template and a checklist before turning it on.
- Two gold models: `deal_subscription_reconciliation` (every won deal and subscription matched by the deal id the subscription carries, with the monthly gap) and `possible_duplicate_company` (flagged records with the name key they share).
- `automations/reconciliation/`: sorts each record into divergence, pending or known case, names who corrects it, proposes the fix, and alerts on divergences. Tolerance and wait are read from the context documents. On today's fictional data it finds one divergence (a deal won in October with no subscription), two pending deals and one known case.
- `automations/duplicate-companies/`: a weekly queue with one proposal per group (keep the oldest record); a person decides, nothing is merged.
- Both run in the Monday workflow and have catalog cards; `cross-cutting-rules` gained the tolerance and the review rule. 7 tests.

## Why
The original's audits (contract value against the CRM, renewal values against billing, duplicate companies) all followed one pattern, and every one of them proposed rather than corrected. This repository counted flags but never listed the records behind them, so nothing could be acted on.

## Result or decision
- Merging is irreversible, so the duplicate queue never merges; the original's later plan to auto-merge only cases with documentary evidence is out of scope here.
- Neither audit writes to a source; the only effect beyond a file is the simulated Slack alert.

## Rules and context changed
`cross-cutting-rules`: the 1-dollar monthly tolerance and the duplicate review rule.

## Follow-ups
Retrieval that reindexes itself, then the business skills and lessons.
