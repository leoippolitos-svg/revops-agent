# ADR-0004: A pull request for every unit of work

- Status: accepted
- Date: 2026-10-29

## Context
Analyses, rule changes and process decisions usually live in chats and slides, then get redone months later because nobody remembers the conclusion.

## Decision
Every unit of work, not only code, ends in a PR with a typed record in `records/`. Records are indexed by the RAG.

## Alternatives considered
- **PRs for code only**: lighter, but the operational memory is lost.

## Consequences
Small overhead per task. In return the agent can answer "was this done before?" and every rule change has an author, a date and a reason.
