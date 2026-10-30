---
date: 2026-10-30
type: app
pr: "#31"
author: Leonardo Ippolito
---

# Lexical retrieval for search_context

## What was done
Built `agent/rag/retrieve.py`: it splits every context document in the index by section heading and ranks the sections with BM25, in plain Python with no new dependency. Built `evals/run_retrieval.py`, which scores Hit@3 and MRR on `evals/retrieval_cases.yaml`. Added 10 tests, ADR-0012, and the README updates. A test now fails CI if the targets are missed.

## Why
The retrieval cases were written but never run, so nothing proved the approach of ADR-0007 worked. This is the smallest real part of the agent, and the one the other tools depend on.

## Result or decision
- First measurement, over the 50 cases: Hit@3 0.980 and MRR 0.898. Targets are 0.90 and 0.75.
- The single miss was "Does MRR include one-time invoices?". The mrr document never said invoices and payments are not MRR, so the content was missing, not the wording. I added the rule to `mrr.md` (and checked the data has no one-time charges) instead of tuning the ranker. After that: Hit@3 1.000, MRR 0.913.
- Read these numbers with care. The cases were written by the same author as the documents, there are 50 of them, and the fix above was prompted by the eval. They show the approach works on this corpus, not that it generalises to questions from other people.
- The index is rebuilt in memory on every call, so there is no half-built index. This differs from the "inside DuckDB" wording of ADR-0007, because the full-text extension needs a download at run time. ADR-0012 records the change.
- Only `search_context`'s retrieval is built. The tool wrapper, the router, `query_gold`, `get_catalog`, `search_records` and the agent loop are not.

## Rules and context changed
`context/concepts/mrr.md`: MRR comes from subscriptions only, never from invoices, payments or one-time charges.

## Follow-ups
Index the catalog descriptions and the records, for `get_catalog` and `search_records`. Collect questions written by someone else and add them to the cases. Add the router and score it.
