---
date: 2026-10-30
type: infra
pr: "#16"
author: Leonardo Ippolito
---

# Close Phase 3: agent rules and eval cases

## What was done
Marked Phase 3 as complete in the README roadmap, with its scope stated plainly: rules and cases, not a running agent.

## Why
The owner scoped Phase 3 to organization and rules inside the repo. The roadmap should say what exists and not imply more.

## Result or decision
Delivered: ADR-0006 and ADR-0007, tool contracts and model tiers (`agent/tools/README.md`), corrected routing examples, 40 retrieval and 40 router eval cases, and `tools/check_evals.py` in the hook, CI, `make check` and setup.
Not delivered, and not claimed: router code, retrieval index, tool implementations, the agent loop, and any measured Hit@3, MRR or router accuracy. The gold model for stage-to-stage conversion mentioned in the first plan is also not built, so the `funnel-diagnosis` skill still has no conversion table behind it.

## Rules and context changed
none

## Follow-ups
Implementing the router, retrieval and tools against these contracts, and scoring them with the case files. A conversion gold model with its context document.
