---
date: 2026-10-31
type: process
pr: "#57"
author: Leonardo Ippolito
---

# Verification: standard, reviewer agents, profile eval, personal-data guard, AI security review

## What was done
- `docs/standards/verification.md`: "whoever builds does not check alone", the list of verifiers with what each does not cover, adversarial review, "green is not enough", false green, and techniques for verifying data (anchors, locks, independent paths, parity, reconciliation by id, open divergence, prompt hash tied to the eval).
- Two coding subagents in `.claude/agents/`: `adversarial-reviewer` (tries to break an analysis or change) and `done-verifier` (checks every "done" claim against the repository with evidence).
- `evals/profile_cases.yaml` and `evals/run_profiles.py`: 12 questions, each accepting a set of plausible intents, checking the documents loaded and the tools offered before any model call. Runs in CI.
- `tools/check_pii.py`: tracked files must hold no e-mail outside `example.com` and no phone number; prints file and line only. Runs in CI.
- `.github/workflows/ai-security-review.yml`: an AI review of each diff, off until a variable and a key exist, with a note to pin the action to a commit before enabling it.

## Why
The original verified everything with a second agent or a script, declared in each verifier what it did not test, and had been burned by a "5 of 5 green" eval that never ran the agent and by an AI review whose findings appeared only after merge. This repository had tests and structure checks, but no adversarial step, no eval of what the agent loads, and no personal-data guard.

## Result or decision
- The profile eval is the deterministic half of the original end-to-end eval: it proves the routing loaded the right context; it does not prove an answer. Its header says so.
- The AI security review has not run; the action is referenced by branch until someone pins it.

## Rules and context changed
None. Standards: verification; team process links the reviewers.

## Follow-ups
The audit pattern and the reconciliation audit, then the retrieval that reindexes itself.
