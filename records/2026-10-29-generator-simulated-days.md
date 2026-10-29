---
date: 2026-10-29
type: data
pr: "#7"
author: Leonardo Ippolito
---

# Generator: simulated time with `--days`

## What was done
The generator now builds the whole simulated world from the seed and writes snapshots of it as of one day, into `data/raw/as_of=YYYY-MM-DD/`. The first run writes the initial load (2025-12-31); `--days N` adds one folder per day after the latest one. Tests grew from 29 to 39.

## Why
The pipeline has to run on a schedule like a real lakehouse, day after day. That needs source exports that change from one day to the next.

## Result or decision
- Snapshots are full exports, like a nightly dump, not change feeds. Bronze will keep every day's export and silver will keep the latest version of each row. This keeps the generator simple and gives silver real deduplication to do.
- A snapshot keeps only rows dated on or before its day. Values that change over time (deal stage and close date, subscription status, invoice status, ticket close date) show their value on that day. The snapshot at the last day of the world is byte-identical to what the generator wrote before this change, which the existing 29 tests confirm.
- The folder name `as_of=<date>` is the batch id for ingestion.
- Adding days never changes a day already written, and the same days give identical files (checked with folder hashes).
- Empty tables are written with their header, so an early snapshot has every file.
- Seed 42: the initial load has 198 deals; two days later 200.
- The answer key (`_issues.json`) covers the whole world and sits once next to the snapshot folders; some issues are not visible yet in an early snapshot.

## Rules and context changed
none

## Follow-ups
Ingestion into bronze reads these folders in date order (next PR). The `contacts.sales_mql_flag` column is the same in every snapshot, even before the contact's form submission; revisit if a time-aware MQL metric needs it.
