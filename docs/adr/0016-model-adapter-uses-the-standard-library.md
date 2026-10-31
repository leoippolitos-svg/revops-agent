# ADR-0016: The model adapter is built by hand on the standard library, and never run here

- Status: accepted
- Date: 2026-10-31

## Context
ADR-0015 left the real model adapter for later. The owner wants the structure in the repository without an API key, so the adapter has to exist, be tested and be safe to leave unused. A provider package would be a new dependency, which needs its own ADR, and would add nothing the tests could use without a key.

## Decision
`agent/model_client.py` implements the loop's `complete` method by sending one HTTPS request to the Messages API with `urllib`, so `requirements.txt` does not change. The network call is one small function (`http_transport`) that tests replace, so request building and reply parsing are proven with no key. The key is read only from the `ANTHROPIC_API_KEY` environment variable named in `connectors/registry.yaml`, never from `.env`, and it travels only in a header. `python agent/agent.py --ask "question"` is the only path to it and stops at once when the variable is empty.

## Alternatives considered
- **The provider's own package**: handles retries and streaming, but is a new dependency that CI could not exercise.
- **Loading `.env` inside the adapter**: friendlier, but the repository's rule is that nothing in an agent session reads `.env`; the owner exports the variable in their own shell.

## Consequences
The request and reply formats are tested against a fake, not against the real API, so a mismatch with the live service would only show on the first real call. There are no retries, no streaming and no cost logging. Until someone runs `--ask` with a key, the answer quality is still unmeasured and the context A/B and skill-trigger evals still cannot run.
