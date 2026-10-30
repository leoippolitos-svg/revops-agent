---
date: 2026-10-30
type: app
pr: "#22"
author: Leonardo Ippolito
---

# Revenue snapshot micro-app: spec, design tokens and a spec checker

## What was done
Followed the `new-micro-app` skill up to the spec step. Wrote `apps/revenue-snapshot/SPEC.md`: a read-only one-page view of MRR, active customers, funnel entries and MQLs, each with its definition and a link to its context document. Added `design-system/tokens.json` (fictional Fernway colors, type and spacing), which the `html-report` skill already referred to but did not exist. Added `tools/check_apps.py` with 7 tests, wired into the hook, CI `standards`, `make check` and `tools/setup.py`.

## Why
Phase 6 is an example of building under the security standard. The standard says the spec is committed before any code, so the spec, and the rule that enforces the flow, come first.

## Result or decision
- The app reads four gold tables through a read-only connection, has no inputs, and never mixes Marketing's and Sales' MQL counts or shows a partial month as a full one.
- The security checklist in the spec is **not ticked**, because nothing is built. `check_apps.py` enforces that: a ticked box on an app that is not marked built is an error, and an app marked built with an unticked box is an error.
- The checker also requires all template sections, gold-only tables that exist in the dbt gold schema, and a "Must never" that forbids writing to a data source.
- No app code exists. The app is specified, not built.

## Rules and context changed
none

## Follow-ups
Build the app against the spec, tick each checklist item with how it was verified, and register any new connection in `connectors/registry.yaml`. A gold data-quality model and the audit skill, and the conversion model, remain open from earlier phases.
