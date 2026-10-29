---
date: 2026-10-29
type: infra
pr: "#13"
author: Leonardo Ippolito
---

# Rendered data catalog and the close of Phase 2

## What was done
Added `tools/build_catalog.py`, which renders every dbt model and column description into one readable page, `docs/catalog.md`, and lists under each table the context documents that use it. `--check` fails when the page is out of date. The check runs in the pre-commit hook, the CI `standards` job, `make check` and `tools/setup.py`. 8 new tests. The README marks Phase 2 as complete and links the catalog.

## Why
The catalog lives in `schema.yml` files, which are fine for dbt and hard for a person to browse. A reader, or a reviewer of the portfolio, should be able to open one page, see what every table and column is, and jump from a table to what it means for the business.

## Result or decision
- The page is generated and never edited by hand, so it cannot drift from the dbt descriptions: CI fails if it is stale, the same pattern as the annotation check.
- Gold comes first because it is the layer the agent reads; silver follows.
- Each table links to the context documents whose annotations mention it, found by scanning the documents. A table no document uses has no context line, which makes missing documentation visible.
- Table cells escape the pipe character, because one description contains it.
- The catalog stays separate from the context documents (ADR-0003): the page says what a column is and points to the document for what it means, and never repeats a rule.

## Rules and context changed
none

## Follow-ups
Phase 3: directives, intent router, RAG and a retrieval eval. The catalog and the context documents are what the router and retrieval will index.
