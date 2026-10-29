---
date: 2026-10-29
type: infra
pr: "#2"
author: Leonardo Ippolito
---

# Pin the Phase 1 dependencies

## What was done
Added `requirements.txt` with exact versions of DuckDB, dbt-core, dbt-duckdb, PyYAML and pytest, and pointed the README quick start at it.

## Why
Phase 1 starts the data pipeline. Pinned versions make results reproducible on any laptop and in CI.

## Result or decision
No new decision: DuckDB and dbt are already covered by ADR-0001 and ADR-0002, and PyYAML and pytest are the tools the repo checks and tests already need. The versions were installed together in a clean virtual environment on Python 3.13; `pip check` reported no conflicts, DuckDB imported and dbt listed the DuckDB adapter. Not yet verified on Python 3.12, which the README and CI use, nor the DuckDB `vss` extension (needed only in Phase 3).

## Rules and context changed
none

## Follow-ups
Install and test on Python 3.12 when CI starts running the pipeline tests. Choose and test the `vss` extension in Phase 3.
