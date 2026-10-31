---
name: new-micro-app
description: Scaffolds a micro-app in apps/ following the spec-driven flow and the security checklist. Use when the user asks for a "micro-app", "internal tool", "small app", "form" or "dashboard app" for the revenue team.
---

# New micro-app

## Steps

Standard and playbook: `docs/standards/apps.md`. Each step below is a step of that playbook.

1. **Diagnose** (step 0): who uses it, which decision it supports, which gold tables it needs, what already exists. Five lines in the spec's Problem section.
2. **Spec** (step 1): copy `apps/_template/` to `apps/<app-name>/` and fill `SPEC.md` and `README.md`. Commit the spec before any code.
3. **Implement** (step 2) the smallest version from the template's `app.py`. Read data only from gold, through `query_gold`.
4. **Test** (step 3): copy `apps/_template/tests_template.py` to `tests/test_<app_name>.py`; cover the main path, an empty result, stale data, escaping, and no form or script.
5. **Harden** (step 4): tick every item of the micro-app checklist in `docs/standards/security.md`; add the app's row to `context/rules/apps.md` and a report document if it shows numbers; register any connection in `connectors/registry.yaml`.
6. **Report** (step 5): paste the checklist, item by item, into the PR and open an `app` PR with `open-pr`.

## Never

- Add write access to a data source without an ADR.
- Put a key or token in front-end code.
