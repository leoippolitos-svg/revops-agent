# ADR-0001: DuckDB as the lakehouse

- Status: accepted
- Date: 2026-10-29

## Context
The project must run on any laptop with one command, with no cloud account, so that a reviewer can clone it and see it working.

## Decision
Use DuckDB, a single local file, with schemas `bronze`, `silver` and `gold`. Vector search uses DuckDB's `vss` extension, so data and RAG chunks live in the same file and reingest can be transactional.

## Alternatives considered
- **Supabase / Postgres + pgvector**: the stack used in the original production agent. Requires an account and a running service; kept as a possible adapter later.
- **Separate vector store (Chroma, LanceDB)**: a second system to run and keep in sync.

## Consequences
Zero setup and fast analytics. Single-writer: fine for a demo, not for concurrent production writes.
