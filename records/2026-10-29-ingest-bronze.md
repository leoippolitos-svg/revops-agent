---
date: 2026-10-29
type: data
pr: "#8"
author: Leonardo Ippolito
---

# Ingestion into bronze

## What was done
Added `pipeline/ingest.py`, which loads the generator's `as_of=<date>` snapshot folders into the DuckDB file `data/lakehouse.duckdb`, schema `bronze`, and `tests/test_ingest.py` with 9 tests. The pipeline README now explains how to run it.

## Why
Bronze is the first layer of the medallion lakehouse; silver and gold build on it. Only ingestion may write to it (`CLAUDE.md`).

## Result or decision
- One table per source file, named `bronze.<source>_<object>` as the naming standard requires, with `_loaded_at`, `_source` and `_batch_id` added.
- Everything is stored as text: bronze mirrors the source and does not guess types. Typing is silver's job.
- Append-only, and every day's full export is kept. A deal that changes stage appears once per batch with the stage it had that day; silver will keep the latest version.
- Idempotent and atomic: a batch already in `bronze._ingestion_log` is skipped, and each batch loads in one transaction together with its log row. The failure test breaks a file half way through a batch, checks that nothing from that batch remains, and loads it normally after the fix.
- With seed 42 the initial load plus two days is about 3,000 rows per batch.
- The ingestion tests load 31 batches once and share the result (about 26 seconds for all 48 tests). Slower than the generator tests, but contained.

## Rules and context changed
none

## Follow-ups
dbt silver: cleaning, typing and keeping the latest version of each row (next PR).
