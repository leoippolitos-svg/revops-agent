---
date: 2026-10-29
type: infra
pr: "#1"
author: Leonardo Ippolito
---

# Close Phase 0

## What was done
Published the repository and switched on every guardrail the standards describe. `main` is now protected by a ruleset: pull request required (zero approvals, since an author cannot approve their own PR), squash merge only, the `secrets`, `rule-zero` and `standards` checks required, no force push, no deletion and no bypass. Pull request creation is limited to collaborators. The `LEAK_TERMS` secret is set for CI, the local `.leak-terms` file is denied to the coding agent in `.claude/settings.json`, and the git author is the GitHub noreply address. The README status badge now says Phase 0 is complete.

## Why
ADR-0005: rules must be enforced by mechanisms, not by prompts. Phase 0 is only done when those mechanisms exist and have been verified, not when they are written down.

## Result or decision
- The leak check ran for real for the first time and found a forbidden term in a code comment, which was fixed before the first commit. This confirms the guardrail works.
- The first CI run happened before the `LEAK_TERMS` secret existed, so its `rule-zero` job had no terms to check. The run on this PR is the first one with the secret in place.
- The skeleton record (`2026-10-29-repository-skeleton.md`) now says it had no PR, because it was the one direct commit to `main`.

## Rules and context changed
none

## Follow-ups
Phase 1: data generator and bronze → silver → gold.
