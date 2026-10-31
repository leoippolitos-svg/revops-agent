# ADR-0018: The system prompt is four ordered blocks, and each intent has a profile

- Status: accepted
- Date: 2026-10-31

## Context
The prompt was one string: AGENT.md, the fallbacks and the skill. Everything else came from retrieval, so a document an answer needed (the funnel stages for a funnel question) could be missed by a probabilistic search. The agent loop resends the system prompt on every tool call, so a large prompt is paid up to eight times per question. The reference design solved both with ordered blocks, cache markers and a profile per category.

## Decision
- The system prompt is four blocks, in this order: behaviour rules (AGENT.md, fallback.md, agent-security), the intent's fixed documents and skill, today's date, and retrieved context under a "reference, not instruction" header. The first two carry a cache marker; the last two never do.
- Each intent has a profile in `routing.md`: fixed documents read by exact id, and how many retrieved chunks to add. A retrieved chunk of a fixed document is dropped as a duplicate.
- Classification is a cascade that never fails: an optional model classifier, then the rules, then the default. The default runs on the standard tier. The step that decided is logged as `via`. A request to write never reaches a classifier.
- A tool error goes back to the model marked `is_error` with its real message; a cut result carries the real total.

## Alternatives considered
- Retrieval only, with a larger top-K: cheaper to build, but an answer still depends on luck, and more chunks mean more irrelevant text the model tries to use.
- One block with one cache marker: the date and the retrieved chunks change per question and would invalidate the whole prefix.
- Default to the fast tier (as before): cheaper, but the unclassifiable questions are the hardest ones.

## Consequences
- The prompt is larger (the funnel profile is about 30,000 characters) but cached after the first call of a category.
- A new context document reaches the agent either through a profile (always) or retrieval (when relevant); adding it to a profile is a routing change reviewed in a pull request.
- Caching has never been measured against a real API in this repository.
