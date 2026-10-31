---
date: 2026-10-31
type: process
pr: "#60"
author: Leonardo Ippolito
---

# Business skills, investigation, continuous learning, multi-agent work, prompt patterns, lessons

## What was done
- Nine business skills in `agent/skills/`: cohort analysis, detect risk, forecast revenue, score deals, cross-source analysis, statistical check, escalate to a human, write-back request and recommend an automation; and `agent/skills/README.md`, the map from a kind of question to a skill, tier and extra documents (the original's route-intent skill).
- Three coding skills in `.claude/skills/`: session closing, learning a new database, and refinement (spec before code).
- Every new skill has a trigger eval in `evals/skills/`.
- Standards: investigation (seven steps, hypotheses to test first), continuous learning (the loop, where each lesson goes, the ladder of strength), multi-agent work (levels, worktrees, fan-out, delegation), and prompt patterns (with versioning and evaluation).
- `docs/lessons-learned.md`: the generic lessons of the original, each as situation, cause, fix and the rule it left here.
- The `new-analysis` skill now points to the skill map and the investigation protocol; `CLAUDE.md` lists the new standards.

## Why
The original had about forty skills and a written way of working with agents: an investigation protocol, a loop that turned every correction into a rule, rules for running agents in parallel, prompt patterns from production, and a long list of lessons. This repository had four business skills and none of the rest.

## Result or decision
- Skills that depend on data not in gold (detect risk needs health, tickets and milestones) say so and stop, instead of reading silver.
- Skills specific to the original business (investor reports, school-specific analyses, tool archives) were not recreated.

## Rules and context changed
None. Standards and skills only.

## Follow-ups
The final README pass and a parity check against the original.
