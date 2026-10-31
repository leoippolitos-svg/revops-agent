# ADR-0024: Automations are code in the repository, not flows in a workflow tool

- Status: accepted
- Date: 2026-10-31

## Context
The reference design ran many of its process automations in n8n: stage auto-advance with a movement log, deactivation after churn, net price recalculation, site qualification and personalised prospecting messages with AI. It worked, and it had costs that showed up in its own records: the prompt running in the tool drifted from the one in the repository and had to be checked by hash, some flows existed only in the tool's instance with no version history, and moving flows between accounts was a project. Today a coding agent writes and maintains this kind of automation as code quickly.

## Decision
- Every automation is Python in `automations/`, scheduled by GitHub Actions when it needs a schedule, with a spec under `docs/standards/automations.md`, tests, the shared write controls, rules read from the context documents, and a pull request for every change.
- A step that uses AI calls the model through the same adapter as the agent, with the prompt in the repository, its hash recorded with each run, its tokens and cost logged, and a scripted model when there is no key.
- The patterns of the reference design's flows are kept as patterns (loud errors, idempotency by id, rate limits, separate trigger and stamp fields, shared sub-steps, AI that never writes directly).

## Alternatives considered
- Recreate the flows as n8n exports: importable and familiar, but untestable in CI, with prompts outside the review flow and a tool to host.
- A mix: n8n for integrations, code for logic: two places to look for one process.

## Consequences
- One place to read, test and review every automation; no instance to host.
- People who do not write code cannot change a flow in a visual editor; changes go through a pull request.
- A workflow tool remains a fair choice for another team; the automation standard says so.
