# ADR-0007: Lexical retrieval first, vectors only if measured

- Status: accepted
- Date: 2026-10-30

## Context
ADR-0001 mentioned DuckDB `vss` for retrieval. Anthropic offers no embeddings API, so vectors would add a second provider or a heavy local model. The corpus is small (a few dozen short documents).

## Decision
Retrieval starts lexical (BM25) inside DuckDB, behind one `retrieve(question, k)` interface, so a vector backend can be swapped in without touching the agent. Vectors are added only if the retrieval eval (`evals/retrieval_cases.yaml`) misses its targets (Hit@3 >= 0.90, MRR >= 0.75) and the misses are about wording, not missing content.

## Alternatives considered
- **Vectors from day one**: more recall on paraphrases, but a new dependency and a new key for a small corpus.
- **Feeding every document to the model**: no retrieval to maintain, but it breaks just-in-time loading and cost grows with the corpus.

## Consequences
No new provider. Paraphrased questions may rank worse, which the eval will show instead of hiding. Reingest stays transactional as in `docs/standards/rag.md`.
