---
name: open-pr
description: Packages finished work into a pull request with its record and context updates. Use when a task is done, when the user says "open a PR", "ship this", "save this work", or after any analysis, automation, context, process, data, app or infra change.
---

# Open a pull request

Standard: `docs/standards/pull-requests.md`.

## Steps

1. Confirm you are on a branch named `<type>/<short-description>`, not `main`.
2. List the business rules this work created or changed. Update each one in `context/` (load `context-docs`).
3. Create the record: copy `records/_template.md` to `records/YYYY-MM-DD-<short-description>.md` and fill every field.
4. Run the checks available in the repo (`python tools/check_skills.py`, and later `make check`). Fix failures before continuing.
5. Commit with a message in the imperative: `context: define MQL for marketing and sales`.
6. Push the branch and open the PR with `gh pr create`, filling `.github/PULL_REQUEST_TEMPLATE.md`.
7. Run the `pr-review` skill on the PR.

## Never

- Push to `main` or force-push.
- Open a PR without a record.
- Leave a changed rule undocumented "for later".

## Example

Work: analysis of a drop in SQL-to-opportunity conversion.
PR: `analysis/sql-to-opp-drop-2026-09`, with the query in `analyses/`, the record, and an update to `funnel-stages.md` because the analysis found a stage was being skipped.
