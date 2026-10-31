---
date: 2026-10-31
type: infra
pr: "#71"
author: Leonardo Ippolito
---

# The full security review pipeline

## What was done
- `.github/workflows/security-review-pipeline.yml`: a reusable pipeline with two jobs. On a pull request, the AI review reads the diff and comments, then `tools/security_review_eval.py` turns HIGH or CRITICAL findings into a red check, a job summary and one Slack alert. On a push to main, `tools/push_scan.py` scans the added lines for credential shapes.
- `.github/workflows/ai-security-review.yml` is now only a switch that calls the pipeline, off until `AI_SECURITY_REVIEW_ENABLED` is true.
- `docs/standards/security-review-pipeline.md`: what it does, what it is not, the design, what the review looks for, secrets, and when it is ready. The verification standard lists the review and the push scan.
- 13 tests in both directions: clean passes, planted secrets (built at run time, so no literal sits in the repository) fail, a missing findings file is a failure and never a pass.

## Why
The original's pipeline was a reusable workflow, an evaluator that turned the check red and alerted in Slack, a push scan and a short switch per app. This repository only had the basic review workflow.

## Result or decision
- The push scan prints the kind of secret, never its value. The evaluator reads only the findings file.
- Nothing runs until the action is pinned, the secret added and the variable set.

## Rules and context changed
None. Standards: security review pipeline, verification.

## Follow-ups
The README pass for this batch.
