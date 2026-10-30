---
date: 2026-10-30
type: app
pr: "#32"
author: Leonardo Ippolito
---

# query_gold, the read-only door to gold

## What was done
Built `agent/tools/query_gold.py`: one SELECT over gold tables in, columns and at most 200 rows out, with a flag when the result was cut. Added ADR-0013, 52 tests in `tests/test_query_gold.py`, one integration test on the real dbt-built lakehouse, and the README updates.

## Why
It is the only tool that touches the database, so its rules cannot live in a prompt. The contract was written in `agent/tools/README.md` and the MCP server README, and nothing enforced it.

## Result or decision
- Two layers. DuckDB's own parser must see exactly one SELECT whose tables are all in gold (table functions and other schemas or catalogs are refused, CTE names defined by the query are fine). Then the connection itself is read-only, has no file or network access, a 512 MB memory cap, locked settings and a 10 second timer.
- Each rule has a test that tries to break it: writes, DDL, ATTACH, COPY, two statements, quoted and upper-case schema names, other catalogs, `information_schema`, a bare name that only exists in silver, file readers, a query that never ends. A separate test shows the connection refuses writes and file reads even if the parser were skipped.
- On the real lakehouse, every gold model can be counted through the tool and `silver.deal` and `bronze.crm_deal` are refused.
- The guard refuses what it cannot prove safe, so table functions such as `range()` are not available to the agent. Scalar functions are not filtered: with external access off, the ones that could leak the environment do not exist, and the rest only compute on rows already in gold.
- Not covered: nothing calls this tool yet, since the agent loop does not exist. The MCP server will import this file.

## Rules and context changed
No business rule changed. ADR-0013 records the design; the README status lines now say `query_gold` is built.

## Follow-ups
Wrap `search_context` as a tool, then `get_catalog` and `search_records`, then the agent loop. The MCP server should import `query_gold` instead of repeating the guard.
