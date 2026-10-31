---
date: 2026-10-31
type: process
pr: "#45"
author: Leonardo Ippolito
---

# Rewrite the README so a newcomer understands the project

## What was done
Rewrote `README.md` for someone who arrives from a link and has never seen the repository. Added what the project is and why it exists, a reading guide by time available, a "see it" section with real command output and a screenshot of the revenue page (`docs/img/revenue-snapshot.jpg`), a table of what is built and what was never run, and a run-it table with one command per piece. The ADR table now lists all 17 decisions, and the structure tree now names `tests/`, `design-system/`, `agent/rag/` and `agent/tools/`.

## Why
The README still said "phase 2 complete" and listed 5 of 17 ADRs, so it hid most of the work. The repository is linked from a personal portfolio site and from job applications, so the first page has to explain the purpose and be honest about the limits.

## Result or decision
- Every number in the README was checked against a run: 435 tests, Hit@3 1.000 and MRR 0.913 on 50 retrieval cases, router accuracy 1.000 on 40 tuned and 27 held-out cases, 8 gold models, 7 context documents.
- The status badge says "built, not run on a real model" instead of a phase number, because that is the claim a reader most needs.
- The screenshot comes from the page rendered against the rebuilt local lakehouse. Rebuilding with `tools/setup.py` also fixed the local lakehouse that predated `data_quality_snapshot`, so the weekly audit now runs locally in dry run.
- No new claim of a model run was added. The `--ask` path is described as built and never run.

## Rules and context changed
none

## Follow-ups
The `analyses/` folder holds only its README. A portfolio reader would learn more from one finished analysis, which is a separate task. Running `--ask` and the first scored evals still needs the owner's key.
