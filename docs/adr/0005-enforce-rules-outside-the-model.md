# ADR-0005: Enforce rules outside the model

- Status: accepted
- Date: 2026-10-29

## Context
Instructions like "never write to the CRM" or "never read secrets" were written in prompts. A prompt can be ignored or overridden.

## Decision
Every critical rule has a mechanical guard: read-only database connections, denied commands and files in `.claude/settings.json`, and CI checks. Prompts explain the rule; mechanisms enforce it.

## Alternatives considered
- **Prompt-only rules**: zero setup, no guarantee.
- **A full harness framework**: powerful, but heavier than this project needs.

## Consequences
A small set of guards to maintain. Rules hold even when the model gets something wrong.
