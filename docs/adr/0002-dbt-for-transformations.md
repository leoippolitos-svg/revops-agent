# ADR-0002: dbt for transformations

- Status: accepted
- Date: 2026-10-29

## Context
Transformations need to be readable, tested and documented, and the documentation should feed the catalog.

## Decision
Use dbt-core with the dbt-duckdb adapter. Models are SQL; tests and column descriptions live in `schema.yml`; those descriptions are the catalog.

## Alternatives considered
- **Plain SQL run from Python**: fewer dependencies, but tests and docs would be hand-built.
- **SQLMesh**: strong, less common in job descriptions.

## Consequences
Industry-standard tooling and free data tests. One more dependency to install.
