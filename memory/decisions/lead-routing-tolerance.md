---
date: 2026-10-31
status: active
decided_by: RevOps lead
---

# Account continuity may pass the routing limit by 5%

## Decision
The account owner keeps a new lead of the same account even at the capacity limit, up to 5% over the limit, rounded down: 31 for Sales, 8 for Enterprise. Past that, a person decides.

## Why
Account continuity and capacity conflicted between the context document and the spec; the owner chose a small tolerance.

## What it changes for the agent
The rule is in the `lead-routing` context document. Reading "5% or so" as 5% of the limit is the builder's interpretation; say so if asked.

## Where the detail is
`records/2026-10-31-lead-routing-continuity-tolerance.md`, PR #44.
