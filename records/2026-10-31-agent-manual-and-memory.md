---
date: 2026-10-31
type: process
pr: "#50"
author: Leonardo Ippolito
---

# Agent manual, security policy, session closing, workspace and memory

## What was done
Rewrote `agent/directives/AGENT.md` on the shape of the original agent's manual: the reading order (company, agent security, routing, OKRs, entities, area, metrics, CRM and data maps), rules it never breaks (data, clarity, coverage, lakehouse, security), access by role, OKR framing, model tiers, and a section for maintainers (session closing, catalog cards, scratch, what the checks really validate). Added the context documents `agent-security` (scope by role, personal data, escalation, injection, never fabricated) and `session-closing` (three destinations, exit test, digest template). Added `WORKSPACE.md`, `BACKLOG.md`, `projects/` with a template and two projects (the agent and the funnel review), and `memory/` with decisions, patterns, benchmarks and a query history. `CLAUDE.md` now requires session closing before a PR is ready.

## Why
In the original, the agent was only as good as its directives, and the directives stayed good because of a fixed reading order and a session-closing rule that sent every finding to a context document or a project digest. This repository had records per PR but no place for work that spans sessions, no memory of decisions the agent should treat as final, and no reading order.

## Result or decision
- Records stay one per PR; project digests carry the story of multi-session work; context documents carry only stable rules.
- The two decisions the owner took today (funnel-review thresholds, routing tolerance) are now memory the agent treats as final.
- The system prompt grows from about 2,600 to 7,500 characters because AGENT.md is fuller. The next PR splits it into cached blocks so the size is paid once per category.

## Rules and context changed
New context documents `agent-security` and `session-closing`; `CLAUDE.md` gains the session-closing requirement.

## Follow-ups
App template and app rules, engineering security rules and team process, then the agent mechanisms.
