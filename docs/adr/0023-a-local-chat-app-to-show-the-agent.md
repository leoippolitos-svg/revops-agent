# ADR-0023: A local chat app shows the agent, with a scripted model when there is no key

- Status: accepted
- Date: 2026-10-31

## Context
ADR-0022 deferred the web chat because it needs a host and a key. That left the agent visible only from the command line, so its mechanisms (routing, profiles, prompt blocks, guarded tools) were hard to show to anyone who does not read code. The apps standard allows only static pages; a chat needs a server and a script, which the standard says needs a decision first.

## Decision
- Build `apps/agent-chat/`: a server on the standard library, listening on 127.0.0.1 only, with one page that runs a small script.
- It runs the real agent loop and returns the trace of each answer. Without a key, a scripted model (`demo_model.py`) with the same method as the real adapter plays the model's part, and every answer says so. `--model` uses the real adapter when a key is set.
- Safety without sign-in comes from the address: nothing outside the machine can reach it. It also checks the Origin of every request, accepts one validated JSON field, sends a strict Content-Security-Policy with no third-party script, builds the page with text only, and logs no question.
- Hosting it for a team (sign-in, allowlist, row-level security, stored conversations) is still ADR-0022.

## Alternatives considered
- A static page with recorded answers: nothing would really run; the trace would be a picture.
- A framework (Flask, FastAPI, a JavaScript front end): a new dependency for one page, against the repository's rule of simple Python first.

## Consequences
- Anyone can clone the repository, build the lakehouse and watch the agent route, load context and call tools on real data, with no account.
- The demo answers are templated from real rows; answer quality still waits for a model.
