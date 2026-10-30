# ADR-0012: BM25 in plain Python for now

- Status: accepted
- Date: 2026-10-30

## Context
ADR-0007 chose lexical retrieval and said it would run inside DuckDB. The DuckDB full-text extension has to be downloaded at run time, which is a network dependency in tests and CI, and the corpus is a few dozen short sections.

## Decision
`agent/rag/retrieve.py` implements BM25 in plain Python with the standard library, behind the same `retrieve(question, k)` interface. The index is built in memory from the files on each call, so there is no stored index that could be half-built, which is what the transactional reingest rule in `docs/standards/rag.md` protects. No new dependency. When the corpus or the latency makes it worth it, the interface lets a DuckDB or vector backend replace this file.

## Alternatives considered
- **DuckDB full-text search**: matches ADR-0007 literally, but needs an extension download. Rejected for now.
- **Vectors**: still rejected until the eval misses its targets for reasons of wording, see ADR-0007.

## Consequences
Retrieval works offline and is deterministic. It rebuilds the index every call, which is fine for this corpus and wrong for a large one. The measured scores are in the record of this change and are re-checked by a test on every CI run.
