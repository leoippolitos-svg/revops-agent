---
date: 2026-10-31
type: infra
pr: "#56"
author: Leonardo Ippolito
---

# On-call agent and watchdog

## What was done
- `oncall/`: `oncall.py problems` lists failing or late items without AI; `prompt.md` is the agent that diagnoses them, may open one fix pull request per item on `oncall/<id>` and asks for actions from a closed list; `oncall.py execute` checks the report, runs only allowed reruns through the write controls and posts one Slack message per item in its thread, without AI.
- `watchdog.py` restarts a late job whose card says `rerun_ok: true` and alerts only when it cannot.
- Workflows `oncall.yml` (after every collection) and `watchdog.yml` (daily), with the permissions each step needs and every write behind a switch. ADR-0021.
- Two new write-back authorizations (`oncall-actions`, `watchdog-recovery`, cap 5 each), a `github-actions` connector, cards for the on-call agent and the watchdog, and `rerun_ok` on the two idempotent jobs. 7 tests.

## Why
The original's on-call agent closed the loop of the run catalog: the collection said what broke, the agent tried to fix what was code, a person got the exact step for the rest, and everything for one problem stayed in one Slack thread. Its watchdog recovered a job that had not run before anyone was paged.

## Result or decision
- The executor trusts nothing the agent writes: unknown items are dropped, an item the agent forgot still gets a line, and the only action is a rerun of the item's own idempotent workflow.
- Nothing writes until a switch is set; the agent step has never run, and no model is called when there is no problem.

## Rules and context changed
`writeback-rules` (two authorizations), connector registry (GitHub Actions), `catalog/README.md` (`rerun_ok`).

## Follow-ups
Verification agents and the AI security review, then the audit pattern and the new reconciliation audit.
