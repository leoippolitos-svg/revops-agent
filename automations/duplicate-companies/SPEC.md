# Possible duplicate companies, Spec

Status: built

## Problem
Two company records with the same name split one account's history, owners and deals. Merging cannot be undone, so it must never be automatic. This automation turns the duplicate flag into a weekly review queue with one proposal per group, for a person to decide. It follows `docs/standards/audits.md`.

## Trigger
Weekly, in the Monday audit workflow, after the lakehouse is rebuilt. Can be run by hand.

## Inputs
- `gold.possible_duplicate_company`: flagged company records with the name key they share.
- `gold.data_quality_snapshot`: the data date.

## Rules
- A group is the records that share a name key (lower case, no spaces at the ends), as `cross-cutting-rules` defines the flag.
- The proposal keeps the oldest record of the group, the likeliest to carry the history; the others are listed for review.
- Each group is decided by a person, never in bulk. An approved merge is done by hand in the CRM.
- The next run is the reconciliation: a merged group leaves the queue.

## Effects
With `--write`: one queue file per data date in `observability/logs/duplicate-companies-<date>.md`. No other effect.

## Failure behavior
A missing lakehouse or table stops the run with exit code 1 and writes nothing. A failure is never reported as "no duplicates".

## Must never
- Write to any data source, merge or delete a company record
- Read from silver or bronze
- Approve a group on a person's behalf

## Dry run
The default: the queue is printed and nothing is written. `--write` writes the queue file.

## Security checklist
Standard: `docs/standards/security.md`, automation checklist.

- [x] Idempotent: running twice does not duplicate effects. One file per data date, overwritten on rerun; tested.
- [x] Retries with backoff, and a cap. Not applicable: no network call.
- [x] Respects rate limits of every API it calls. Not applicable: it calls no API.
- [x] Failures are logged and alerted, never swallowed. A missing table exits with code 1; tested.
- [x] Credentials scoped to the minimum and registered. None; it reads the registered local lakehouse.
- [x] Dry-run mode for anything that would write to an external system. Dry run is the default; tested.
