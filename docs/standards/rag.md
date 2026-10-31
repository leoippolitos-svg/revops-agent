# RAG

## What is indexed

Five categories (`agent/rag/corpus.py`), after the reference design's memory taxonomy:

| Category | Source | Chunking | Searched |
|---|---|---|---|
| `domain` | concept documents | by `##` section, long sections by paragraph | by default |
| `reference` | the other context documents: company, areas, metrics, maps, reports, rules | same | on request; intents load the ones they need whole, by id |
| `decisions` | `docs/adr/`, `memory/decisions/` | same | on request |
| `conventions` | `docs/standards/` | same | on request |
| `incidents` | project digests (`projects/*/CONTEXT.md`), skipped while empty | same | on request |
| records | `records/` | one chunk per record | through `search_records` |

Each chunk keeps its document id, status, category and section heading.

Why `reference` is not in the default search: tried there, the long area and metrics documents pushed the definitions out of the top 3 (Hit@3 fell to 0.88, MRR to 0.68). What an intent always needs is loaded by id instead (the category profiles in `routing.md`), because retrieval is probabilistic.

## Reingest

The lexical search reads the files on every call, so a merged change is searchable at once and nobody ever queries a half-built index. `agent/rag/ingest.py` keeps an incremental index (`data/rag-index.json`) for a future embedding step: per file, the SHA-256 of its text with line endings normalised and its chunks. Only changed files are re-chunked, files that left the corpus are removed, and the index is written to a temporary file and swapped in whole. `.github/workflows/rag-reingest.yml` runs it after every merge that touches the corpus and scores retrieval, routing and profiles again.

## Retrieval

Just in time: the agent first sees the index (`context/index.yaml`) and catalog names, then retrieves only the documents the question needs. Nothing is preloaded "just in case".

## Evaluation

| Metric | Meaning | Target |
|---|---|---|
| Hit@3 | Expected document appears in the top 3 | ≥ 0.90 |
| MRR | How high the expected document ranks | ≥ 0.75 |
| Router accuracy | Question sent to the right intent | ≥ 0.90 |

The eval set has around 40 questions, each with its expected document and intent, in `evals/`. A PR that lowers a metric must explain why.
