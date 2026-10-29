# RAG

## What is indexed

| Source | Chunking | Why |
|---|---|---|
| Context documents | By section heading | Definitions and rules |
| Catalog descriptions | One chunk per model | Lets the agent find the right table |
| Records | One chunk per record | Past work and conclusions |

Each chunk keeps metadata: source path, document id, section, `last_reviewed`.

## Reingest

Reingest runs inside **one transaction**: delete old chunks, insert new ones, commit. If anything fails, roll back and the previous index stays intact. Nobody ever queries a half-built index.

## Retrieval

Just in time: the agent first sees the index (`context/index.yaml`) and catalog names, then retrieves only the documents the question needs. Nothing is preloaded "just in case".

## Evaluation

| Metric | Meaning | Target |
|---|---|---|
| Hit@3 | Expected document appears in the top 3 | ≥ 0.90 |
| MRR | How high the expected document ranks | ≥ 0.75 |
| Router accuracy | Question sent to the right intent | ≥ 0.90 |

The eval set has around 40 questions, each with its expected document and intent, in `evals/`. A PR that lowers a metric must explain why.
