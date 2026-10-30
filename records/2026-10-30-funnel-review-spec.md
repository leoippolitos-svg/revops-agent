---
date: 2026-10-30
type: automation
pr: "#28"
author: Leonardo Ippolito
---

# Weekly funnel review, specified

## What was done
Wrote `automations/funnel-review/SPEC.md` ("Status: specified, not built", checklist unticked). Added `tools/check_automations.py` and its tests, which validate every automation spec the way `check_apps.py` validates apps; it is wired into the pre-commit hook, CI, the Makefile and `tools/setup.py`. Added the maturity rule and the minimum sample to `funnel-stages.md`.

## Why
The funnel review was a name in `automations/README.md`. The spec says what triggers it, which gold tables it reads, what it writes and what it must never do. The checker closes the gap noted before: automation specs were not validated by anything.

## Result or decision
- The review follows the `funnel-diagnosis` skill, compares only mature cohorts (90 days after the month ends) with at least 20 qualified deals per period, and says "nothing changed" instead of inventing a bottleneck. The two thresholds live in the context document, not in code.
- It needs judgment, so it is the agent's job, not a script. ADR-0009 already names a scheduled cloud agent as an option for that; nothing new is decided here.
- The effect is a report file in `observability/logs/`; nothing is sent anywhere.
- Not built, not run. The checklist stays unticked and the checker refuses a ticked box on an unbuilt automation (tested).
- Checked: `check_automations.py` passes on the audit and the new spec, with 7 tests.

## Rules and context changed
`context/concepts/funnel-stages.md`: cohort maturity (90 days) and the 20-deal minimum for a comparison.

## Follow-ups
Build it once the agent exists. Specs for `lead-routing` and `closed-won-provisioning` are next.
