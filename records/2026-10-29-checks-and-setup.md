---
date: 2026-10-29
type: infra
pr: "#11"
author: Leonardo Ippolito
---

# Checks, one-command setup and the close of Phase 1

## What was done
Added `tools/check_context.py` (context documents and dbt catalog must agree), `pipeline/checks/daily_check.py` (today's bronze batch against yesterday's), `tools/setup.py` and a `Makefile` for a one-command build, 14 tests in `tests/test_checks.py`, and wired the context check into the pre-commit hook and the CI `standards` job. The README now marks Phase 1 as complete and documents the one command.

## Why
The standards promised checks that did not exist yet: annotations that resolve, a described catalog, and a daily comparison. Phase 1 is only done when the pipeline can be built from nothing with one command and guarded against silent breakage.

## Result or decision
- `check_context.py` fails on: a context document missing or with a mismatched id or status, an annotation that points at nothing, a dbt model or column without a description, and a model file with no catalog entry (or the reverse). It passes on the real repository and fails on each broken case in the tests.
- `daily_check.py` errors when a table loses rows or disappears between two daily exports, and warns on a swing of more than 20% in a day for tables of 100 rows or more. Exports are full copies, so a table can only keep or gain rows. It exits with code 1 on any error, so a scheduler can alert on it.
- `tools/setup.py` runs generate, ingest, dbt build and the checks, stopping at the first failure. It is a Python script because `make` is not installed on the author's Windows machine; the `Makefile` only calls it. Run end to end it builds the whole lakehouse (17 models, 78 dbt tests passing).
- The setup script hands every step the same absolute database path through `LAKEHOUSE_PATH`: dbt resolves a relative path from the folder it runs in, which sent the first attempt to the wrong place.
- Not verified: the `Makefile` itself (no `make` here), and a build from a fresh clone on another machine. The tests job is not yet a required check of the `main` ruleset; that is a repository setting the owner decides.

## Rules and context changed
none

## Follow-ups
Phase 2: review the four draft context documents with their owners, decide which MQL flag is canonical, write the entry and exit criteria of each funnel stage, and add the `cross-cutting-rules` document. Add `tests` to the required checks of `main`.
