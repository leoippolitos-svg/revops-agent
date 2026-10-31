---
date: 2026-10-31
type: app
pr: "#59"
author: Leonardo Ippolito
---

# Retrieval corpus by category, incremental reingest

## What was done
- `agent/rag/corpus.py` defines five categories: `domain` (concepts, the default), `reference` (company, areas, metrics, maps, reports, rules), `decisions` (ADRs and memory decisions), `conventions` (standards) and `incidents` (project digests). Files are chunked by `##` heading and long sections by paragraph.
- `retrieve` and the `search_context` tool take a category; an unknown one is refused.
- `agent/rag/ingest.py` keeps an incremental index by SHA-256 with line endings normalised: only changed files are re-chunked, removed files leave the index, and the file is swapped in whole.
- `.github/workflows/rag-reingest.yml` runs after every merge that touches the corpus and scores retrieval, routing and profiles again. The RAG standard explains all of it. 6 tests.

## Why
In the original, the corpus was categorised (domain, decisions, conventions, incidents), project digests were searchable so the agent knew what had been tried, the index was incremental by hash with CRLF normalised, and a merge to main reingested automatically.

## Result or decision
- Mixing the area and metrics documents into the default search was tried and lowered Hit@3 to 0.88 and MRR to 0.68, below target. They became the `reference` category, reached through the intent's fixed documents or an explicit search. Retrieval stays at Hit@3 1.000 and MRR 0.893.
- The index is not used by the lexical search, which reads files directly; it is where an embedding step would go, and nothing is embedded today.

## Rules and context changed
None. Standard: RAG.

## Follow-ups
Business skills, the investigation protocol, the continuous-learning loop and the lessons learned.
