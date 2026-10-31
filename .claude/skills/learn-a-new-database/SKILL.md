---
name: learn-a-new-database
description: "A method to learn an unfamiliar database before answering from it: inventory, grain, keys, freshness, traps, and a written map. Use when the user brings a new source, schema or warehouse, asks how a database works, or wants to start analysis on data nobody has mapped."
---

# Learn a new database

## Steps

1. Inventory: list schemas and tables with row counts and the date of the newest row. Read-only, always.
2. Grain: for each table you need, find what one row is and its key; count rows per key to prove it.
3. History: is it a snapshot, a change log or a current-state table? A change log needs the latest version per key before any join.
4. Keys and joins: sample ten keys on both sides of every join; count rows before and after it.
5. Traps: sentinel dates, labels that do not exist (a "false zero"), status that rewrites the past, soft deletes.
6. Anchors: reproduce three numbers the business already trusts; if they do not match, stop.
7. Write the map: a data map document with grain, joins, a model query and validation queries, and open a `data` pull request for the models it needs.

## Example

A new billing export: invoices are a change log, so the latest version per invoice is taken first; the monthly total then matches Finance's number within 1%.

## Troubleshooting

- **The anchors do not match**: suspect the method (join, filter, window) before the business.
