---
date: 2026-10-31
type: process
pr: "#51"
author: Leonardo Ippolito
---

# App standard and template, engineering security rules, team process

## What was done
- `docs/standards/apps.md`: where apps live (one folder each, README, a row in the `apps` context document), the one stack, and the playbook from step 0 (diagnose) to step 5 (report), with the mistakes that cost production in the reference design.
- `apps/_template/` gained `app.py`, `README.md` and `tests_template.py`; `apps/revenue-snapshot/README.md` was added. `tools/check_apps.py` now fails when an app has no README or no row in `context/rules/apps.md`. The `new-micro-app` skill follows the playbook.
- `docs/standards/security.md` gained the twenty engineering rules, the practices that go with them, what to do when a request breaks a rule, the review checklist, the home penetration test and secret rotation.
- `docs/standards/team-process.md`: the task cycle, who approves, the six laws of git, "green is not reviewed" and twenty working principles.
- `tools/check_derived.py` warns when a condensed copy no longer matches its source (hash with line endings normalised); first copy: `docs/standards/security-summary.md`. It runs in CI as a warning.
- The PR template gained a Test plan section; `CLAUDE.md` lists the two new standards.

## Why
The original agent had a micro-app pattern with a template and a playbook, twenty security rules born from incidents, a written team process and short rule copies kept in sync with their sources. This repository had a spec template and a checklist, but none of the rest.

## Result or decision
- The rules are generalised: no employer, product, or tool-specific detail. Rules about sign-in, row-level security and per-app credentials wait for the first app that has those surfaces; the current stack is a static page with no inputs.
- The derived check warns instead of failing, as in the original: a source can change without touching its summary, and a person decides.

## Rules and context changed
No business rule. Standards: apps, security, team process, PR template.

## Follow-ups
Agent mechanisms: prompt blocks and category profiles, answer rules, the map tool, cost per answer.
