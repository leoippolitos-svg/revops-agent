---
date: 2026-10-29
type: infra
pr: "#4"
author: Leonardo Ippolito
---

# Run pytest in CI

## What was done
Added a `tests` job to `.github/workflows/ci.yml` that installs `requirements.txt` on Python 3.12 and runs `python -m pytest`. The `standards` job now installs `requirements.txt` too, instead of an unpinned `pyyaml`.

## Why
The generator tests from the previous PR only ran on a laptop, and CI used different package versions than local development. Tests that CI does not run protect nothing, and the dependencies were pinned in the previous PR for exactly this reason. This also covers Python 3.12, which the README and CI use but local checks had not (the first run here was on 3.13).

## Result or decision
- `tests` is a separate job, not a step inside `standards`, so a failure says what failed.
- It is not a required check yet. A check can only be required after it has run once, and changing the `main` ruleset is the owner's call; see Follow-ups.
- The `permissions:` block suggested in the Phase 0 review is left out on purpose: the gitleaks action in the required `secrets` job may need more than read access, and breaking a required check is worse than the nit. It gets its own PR with a test of that job.

## Rules and context changed
none

## Follow-ups
Add `tests` to the required checks of the `main` ruleset once it has run. Add a minimal `permissions:` block in a separate PR and confirm `secrets` still passes.
