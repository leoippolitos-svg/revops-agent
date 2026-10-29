---
date: 2026-10-29
type: data
pr: "#9"
author: Leonardo Ippolito
---

# dbt silver layer

## What was done
Created the dbt project in `pipeline/dbt/` with 13 silver models (one per entity), a `latest_version` macro, the catalog descriptions in `schema.yml`, and `tests/test_dbt_silver.py`, which builds bronze from generated data, runs `dbt build` and checks the result.

## Why
Bronze holds every daily export as text. Silver turns it into one clean, typed row per entity, which gold builds on.

## Result or decision
- Silver keeps the most recent version of each row (by batch id) and casts text to integers, dates and booleans; empty text becomes null.
- The layer is the schema (`silver.company`), not a name prefix: a `generate_schema_name` macro overrides dbt's default `main_silver`, and a test checks it.
- Data-quality issues are flagged, not removed: `company.is_possible_duplicate`, `deal.has_company`, `subscription.has_matching_deal`. Choosing which duplicate wins, or what a deal without a company counts as, is a business rule for a context document, not for silver.
- Every model has a tested primary key (`unique`, `not_null`), accepted-value tests for status-like columns, and relationship tests where the data has no planned issue. Relationships that the generator breaks on purpose (deal to company, subscription to deal) are covered by the flags instead of a failing test.
- `dbt build` on 10 simulated days passes 13 models and 56 tests. The Python test also confirms one row per entity, latest-version stage, column types, and that planted issues are visible.
- The test releases dbt's connection (`cleanup_connections`, `reset_adapters`) because dbt runs in the test process and DuckDB allows one configuration per file at a time.
- No new dependency: dbt and the DuckDB adapter were added in the pinned requirements PR (ADR-0002).

## Rules and context changed
none. Silver adds no business definition; the first context documents arrive with gold, which introduces concepts such as MRR and active customer.

## Follow-ups
Gold models and their context documents (next PR). CI runs the dbt test through pytest; a separate `dbt build` step can wait until there is more than one layer to build.
