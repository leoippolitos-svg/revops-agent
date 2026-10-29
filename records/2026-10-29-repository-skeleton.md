---
date: 2026-10-29
type: infra
pr: "none"
author: Leonardo Ippolito
---

# Repository skeleton and standards

## What was done
Created the folder structure, the standards for context documents, data modeling, skills, pull requests, security, connectors and RAG, five ADRs, the coding-agent skills, the agent directives and the first draft context document.

## Why
Rebuild a production RevOps agent as a public reference project, on a fictional company, with the context and gold layers the original lacked.

## Result or decision
Standards and guardrails are in place before any code. DuckDB and dbt chosen (ADR-0001, ADR-0002). Every unit of work goes through a PR (ADR-0004). This skeleton is the one exception: it was the first commit on `main`, made before the repository existed on GitHub, so it has no PR.

## Rules and context changed
- `context/concepts/active-customer.md` — first draft, annotations pending the gold layer.

## Follow-ups
Phase 1: data generator and bronze → silver → gold.
