# ADR-0013: query_gold checks the parsed query and the connection

- Status: accepted
- Date: 2026-10-30

## Context
ADR-0006 says `query_gold` reads only the gold schema and only runs SELECT. Searching the SQL text for the word "silver" is easy to get around (quoted names, other catalogs, table functions that read files), and a rule that lives only in a prompt is a wish (`docs/standards/security.md`).

## Decision
`agent/tools/query_gold.py` has two layers that do not depend on each other. First, DuckDB's own parser: exactly one statement, of type SELECT, and the parsed tree (`json_serialize_sql`) may reference only tables that exist in `gold`. Any other schema, any other catalog and any table function (`read_csv`, `duckdb_tables()`) is rejected. Second, the connection: the file is opened read-only, `enable_external_access` is off, memory is capped, the configuration is locked, and a 10 second timer interrupts the query. Results stop at 200 rows and say so. No new dependency.

## Alternatives considered
- **Searching the SQL text for schema names**: simple, but it rejects honest queries and misses dishonest ones.
- **A SQL parsing library**: more detail, but a new dependency and a second parser that can disagree with the one that runs the query.
- **A database role with grants on gold only**: the right answer on a server database. DuckDB has no roles, so the two layers above stand in for it.

## Consequences
The guard rejects what it cannot prove safe, so some harmless queries need rewriting (no table functions, for example). The tests in `tests/test_query_gold.py` are the proof of each rule, and the MCP server reuses this same file instead of writing its own guard.
