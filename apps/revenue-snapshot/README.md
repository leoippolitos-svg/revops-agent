# Revenue snapshot

## What it is
One read-only page for revenue leaders: MRR, active customers, funnel entries and MQLs by month, each with its definition. It answers the four Monday questions on one page; it does not filter, edit or export.

## How to run it
`python apps/revenue-snapshot/snapshot.py --out snapshot.html`. No environment variable is needed: it reads the local lakehouse read-only.

## Data
Four gold tables through `query_gold`, listed in [SPEC.md](SPEC.md). How each number is computed: the `report-revenue-snapshot` context document.

## Tests
`tests/test_revenue_snapshot.py`: partial month, Sales MQL shown only as "Sales agrees", missing or stale gold, escaping, no form or script.

## Owner and status
RevOps lead. Built and tested (2026-10-31); never hosted or opened in a real browser by a user.
