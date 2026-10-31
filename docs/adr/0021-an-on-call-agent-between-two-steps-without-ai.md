# ADR-0021: An on-call agent between two steps without AI, and a watchdog

- Status: accepted
- Date: 2026-10-31

## Context
The run catalog says what is failing or late, but someone has to look and act. The reference design added an on-call agent: after each collection, list the problems without AI, let an agent diagnose and fix what is code, then run only the allowed actions and talk in Slack, without AI. A watchdog restarted a daily job that did not run before alerting anyone.

## Decision
- `.github/workflows/oncall.yml` runs after every collection, in three steps: `oncall/oncall.py problems` (no AI); the agent with `oncall/prompt.md`, through Claude Code, only when a problem exists, `ONCALL_AGENT_ENABLED` is true and the key secret exists, with a shell limited to `gh run`, `gh pr`, `git` and `python`; then `oncall/oncall.py execute` (no AI).
- The agent may open one pull request per item on `oncall/<id>` and ask for actions from a closed list. The only action is `rerun`, and only for a workflow whose card says `rerun_ok: true`. It never merges, never touches workflows, rules, credentials or data.
- The executor trusts nothing in the report: it drops entries for unknown items, refuses actions off the list, runs reruns through the write controls (`oncall-actions`), and posts one message per item in that item's Slack thread.
- `oncall/watchdog.py` (daily) restarts a late `rerun_ok` job through the write controls (`watchdog-recovery`) and alerts only when recovery is not allowed or fails.

## Alternatives considered
- Let the agent run actions itself: one prompt injection in a log away from an action nobody chose.
- No agent, alerts only: someone reads every failure by hand, which is what the catalog was meant to end.

## Consequences
- A collection with no problem never calls a model, so the cost is paid only when something breaks.
- Both workflows run in this repository, but every write is off until its variable is set; the agent step has never run.
