---
date: 2026-10-30
type: data
pr: "#15"
author: Leonardo Ippolito
---

# Eval case files and their offline validator

## What was done
Added `evals/retrieval_cases.yaml` (40 questions, 8 per context document, each with its expected document) and `evals/router_cases.yaml` (40 questions, 5 per intent). Added `tools/check_evals.py`, which validates both files: at least 40 cases, expected documents exist in `context/index.yaml`, intents exist in `routing.md`, every document and intent is covered, no duplicate questions. It runs in the pre-commit hook, CI `standards`, `make check` and `tools/setup.py`. 4 tests.

## Why
Phase 3 delivers the rules and the measuring sticks, not a running agent. A case file with a typo would score zero silently later, so the files are validated now.

## Result or decision
- The cases are written by hand for Fernway; they are the contract future retrieval and router code is judged against (targets in `docs/standards/rag.md`).
- Nothing is scored yet. No Hit@3, MRR or router accuracy exists, and none is claimed.
- Retrieval cases only target context documents. Catalog and record retrieval cases can be added when those indexes exist.

## Rules and context changed
none

## Follow-ups
Close Phase 3 in the README and roadmap. Scoring code is part of whichever phase implements retrieval and the router.
