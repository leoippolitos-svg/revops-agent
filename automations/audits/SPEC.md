# Weekly data-quality audit, Spec

Status: built

## Trigger
Every Monday morning (UTC), and on demand. Scheduled by `.github/workflows/weekly-audit.yml`.

## Inputs
One gold table, read-only: `gold.data_quality_snapshot`.

## Rules
- The audit reports every flag count next to its total and its share.
- The audit raises "attention" for a flag only when its count is higher than in the previous report. A count that is steady or falling is reported, not raised.
- The first report has nothing to compare with, so it raises nothing.
- Closed won deals without a subscription include deals won in the last two weeks; that is normal and is stated in the report, see the context document `cross-cutting-rules`.
- What each flag means and who owns the fix is in `cross-cutting-rules`. The audit does not repeat those rules.

## Effects
Writes one file, `observability/logs/audit-<as_of date>.md`, only when run with `--write`. This is the simulated alert channel. Nothing is sent to any external system and no record is changed.

## Failure behavior
If gold or the snapshot table is missing, the audit exits with an error and a message, and writes nothing. An error is never reported as "no problems".

## Must never
- Write to any data source
- Read from silver or bronze
- Delete or merge the flagged records
- Send a message to an external system

## Dry run
Dry-run is the default: the report is printed and no file is written. `--write` turns the effect on. Running twice for the same data date overwrites the same file, so effects are not duplicated.

## Security checklist
Standard: `docs/standards/security.md`, automation checklist.

- [x] Idempotent: running twice does not duplicate effects. Verified by a test that writes twice and finds one file.
- [x] Retries with backoff, and a cap. Not applicable: there is no network call, only a local read-only file.
- [x] Respects rate limits of every API it calls. Not applicable: it calls no API.
- [x] Failures are logged and alerted, never swallowed. A missing table exits with code 1 and a message; tested.
- [x] Credentials scoped to the minimum and registered. It uses none; it reads the local lakehouse, already registered as `lakehouse`.
- [x] Dry-run mode for anything that would write to an external system. Dry-run is the default, and it writes no file; tested.
