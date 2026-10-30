# ADR-0009: Scheduled work is an automation, not a skill

- Status: accepted
- Date: 2026-10-30

## Context
The weekly data-quality audit has to run without a person asking. A skill is a method the agent loads when a question calls for it; it schedules nothing and does not run by itself. The audit is also a set of counts, which need no model to compute.

## Decision
Recurring work is an automation: a script under `automations/`, a spec, tests, and a trigger. For the audit the trigger is a scheduled GitHub Actions workflow, which rebuilds the fictional lakehouse, runs the script and keeps the report as an artifact. Skills stay for interpretation on demand: `data-discrepancy` is what the agent uses when someone asks why a flag count is what it is.

## Alternatives considered
- **A skill that the agent runs weekly**: nothing triggers it, and a model would do work a query does exactly.
- **A scheduled cloud agent (a Claude Code routine)**: possible, and it would clone the repo and run the same script. It adds a dependency on a research-preview feature and a model run for a deterministic job, so it is not the first choice. It stays an option for work that needs judgment, such as a written weekly funnel review.
- **A consumer always-on agent product**: a different kind of product, in a limited preview, not something this repository can depend on.

## Consequences
The audit is deterministic, tested and visible in the repo. Anything that must run on a schedule gets a workflow and a spec, and the agent never needs to be running for it to happen. Hosting beyond GitHub Actions, for example a self-hosted deployment for demos, is a separate decision for a later ADR.
