---
name: fix-failing-data-check
description: Diagnoses and fixes a failing pipeline check, such as lost rows, a missing table, a dbt test failure or a stale catalog. Use when the daily check, tools/setup.py, dbt build or CI reports an error, or when the user says "the pipeline broke", "numbers look wrong after the load" or "the check failed".
---

# Fix a failing data check

## Steps

1. Read the failure in full and name the failing layer: generator, ingestion (bronze), silver, gold, or a repo check.
2. Reproduce it with the smallest command. The daily check is `python pipeline/checks/daily_check.py --db <path>`. It reports an ERROR when rows are lost or a table is missing between the last two batches, and a WARN when a table of at least 100 rows grows by more than 20%.
3. Look at `bronze._ingestion_log` to see which batches loaded and when.
4. Classify the cause:
   - **Source changed** (a batch is smaller or has a new shape): decide if it is real or a source fault.
   - **Ingestion bug**: fix `pipeline/ingest.py`.
   - **Model bug**: fix the dbt model or its test.
   - **Definition change**: update the context document first, then the model.
5. Fix upstream of the symptom. Never patch a gold number by hand.
6. Add or tighten a test so this failure is caught next time.
7. Run `python tools/setup.py` end to end with an absolute `LAKEHOUSE_PATH`.
8. Open the PR with `open-pr`, type `data`. The record states the cause and how it is now caught.

## Example

ERROR: a CRM bronze table has fewer rows than the previous batch. Cause: the export filtered by a date. The fix is in the generator snapshot, plus a test that deal counts never go down between consecutive batches.

## Troubleshooting

- **WARN only**: growth over 20% may be real. Compare with the funnel before changing anything.
- **dbt resolves the wrong database**: pass an absolute `LAKEHOUSE_PATH`.
- **The database is locked**: another process holds it. Close it and rerun.

## Never

- Edit bronze by hand. Bronze is written only by ingestion.
- Delete rows to make a check pass.
