---
date: 2026-10-31
type: process
pr: "#63"
author: Leonardo Ippolito
---

# Automation documentation standard, and why automations are code

## What was done
- `docs/standards/automations.md`: every automation spec now explains the problem, why it exists as a process, the expected gain with its calculation and assumptions (labelled as a projection), a Mermaid diagram of how it works, where AI enters, tokens and cost, and monitoring, before its trigger, rules and limits. It also lists the patterns kept from the reference design's workflow-tool flows.
- The six existing specs gained those sections. `tools/check_automations.py` requires them, and checks that gains say "projection" and that the flow is drawn; two tests.
- `automations/README.md` is now an index with trigger, goal, expected gain and AI per automation, as the original's flow index was.
- ADR-0024: automations are code in the repository, not flows in a workflow tool. `CLAUDE.md` and the `new-automation` skill point to the standard.

## Why
The owner wanted every automation documented so anyone can see the problem, why the process exists, the gain and the design, the way the original documented its n8n flows; and agreed that today these flows are better built as code than in a workflow tool.

## Result or decision
- Every gain is a projection on fictional volumes, with the assumption next to the number and how it will be measured.
- The five flows inspired by the original's n8n workflows come next, as Python automations under this standard.

## Rules and context changed
None. Standard: automations; specs of the six automations.

## Follow-ups
Onboarding auto-advance with a movement log, deactivation after churn, deal amount recalculation, site qualification and prospecting drafts with AI.
