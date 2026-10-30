---
date: 2026-10-30
type: app
pr: "#34"
author: Leonardo Ippolito
---

# get_catalog and search_records

## What was done
Built `agent/tools/get_catalog.py` and `agent/tools/search_records.py`, plus the record search behind it in `agent/rag/record_search.py`. The two search tools now share one input check (`check_search_input` in `search_context.py`). Added tests in `tests/test_catalog_and_records_tools.py` and updated the contract rows and status lines. With this, all four agent tools have code.

## Why
The router sends diagnosis and data-quality questions to `get_catalog` and `search_records`, and the skills name them. They were contracts only.

## Result or decision
- `get_catalog` reads the dbt `schema.yml` files through the same loader that renders `docs/catalog.md`, so the page and the tool cannot disagree. A test makes the database fail loudly if it is ever opened. A name that is not in the catalog (including `bronze.*`, injection text and path text) is rejected and the gold models are listed so the agent can retry. A bare name means the gold model.
- `search_records` ranks each record as one chunk with the same BM25 as the context documents, and returns title, date, type, PR and the "Result or decision" section. The folder README and the template are not records. A test checks that every real record has a title, a date and a conclusion, so a malformed record fails CI.
- Measured: 10 questions about the real records, the right record in the top 3 for all 10. I wrote those questions after reading the records, so this shows the search works on them, not that it generalises. Question wording that is a phrase ("time in stage") still ranks by single words: the time-in-stage record came second to the conversion record for one query I tried.
- Not covered: no agent loop calls these tools; records are not scored in `evals/`, only in a test.

## Rules and context changed
No business rule changed. The `get_catalog` and `search_records` rows in `agent/tools/README.md` state the new input and output details.

## Follow-ups
The agent loop and the router, which need a model call and so a decision about running them without a key. Questions about records written by someone else.
