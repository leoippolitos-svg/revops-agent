---
date: 2026-10-30
type: infra
pr: "#14"
author: Leonardo Ippolito
---

# Agent rules: tools, model tiers and retrieval approach

## What was done
Added ADR-0006 (four read-only agent tools and two model tiers) and ADR-0007 (lexical retrieval first, vectors only if measured). Added `agent/tools/README.md` with the contract of each tool, the call budget and the logging rules. Fixed the routing examples so they use metrics that exist in gold (MQLs, MRR) instead of SQLs and win rate.

## Why
Phase 3 is scoped to organization and rules inside the repo, not to a running agent. The rules must exist, and be reviewable, before any code implements them.

## Result or decision
- The agent surface is four read-only tools. A fifth needs a new ADR.
- Retrieval starts lexical because Anthropic has no embeddings API; this refines the `vss` mention in ADR-0001.
- Nothing here calls a model, so nothing was measured. Router accuracy and retrieval metrics stay unmeasured until case files and code exist.

## Rules and context changed
none

## Follow-ups
Eval case files (`retrieval_cases.yaml`, `router_cases.yaml`) with an offline validator, then the Phase 3 close.
