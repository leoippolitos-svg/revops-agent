# ADR-0015: The agent loop does not depend on a model provider

- Status: accepted
- Date: 2026-10-30

## Context
The agent needs a model, and a model needs a provider package and an API key. CLAUDE.md asks for an ADR for every new dependency, the key must stay in `.env` that the coding agent never reads, and the loop's guarantees (budget, allowed tools, refusing to act, what is logged) must hold for any model.

## Decision
`agent/agent.py` talks to a model through one method, `complete(model, system, messages, tools)`, and imports no provider. The budget, the tool allow-list, the refusal to act and the log are all enforced in the loop, so no prompt has to be obeyed for them to hold. Tests use a scripted stand-in. A real adapter (the provider package plus a key from the environment) is a separate change with its own ADR, and is not part of this one.

## Alternatives considered
- **Importing the provider package now**: gives a runnable agent, but adds a dependency, needs a key to test, and could not be checked in CI.
- **Leaving the loop out until a key exists**: nothing about budgets and tool limits would be tested until then.

## Consequences
The rules of the loop are proven in CI with no key. Nobody has run the agent against a real model, so answer quality is not measured and the context A/B and skill-trigger evals still cannot run. Writing the adapter is small, but it is the step that costs money and needs the owner's key.
