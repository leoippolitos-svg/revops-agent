---
date: 2026-11-01
type: process
pr: "#73"
author: Leonardo Ippolito
---

# Nothing runs on its own: scheduled workflows switched off

## What was done
- These six workflows were switched off in GitHub Actions: daily automations, weekly audit, run catalog collector, watchdog, on-call agent and retrieval reingest. The command used was `gh workflow disable`.
- The README status table no longer says those jobs are scheduled. A short paragraph now explains that the repository is meant to be read, that only CI runs on pull requests, and how to switch a workflow back on.

## Why
The owner wants the repository to be a portfolio to read, not a system that keeps running and uses Actions. The workflow files stay in the repo because they show the design.

## Result or decision
- CI stays on for pull requests, because the main-branch ruleset requires its checks.
- The AI security review stays wired, and it skips itself while its switch is off.

## Rules and context changed
None.

## Follow-ups
None. Re-enabling any workflow is the owner's call.
