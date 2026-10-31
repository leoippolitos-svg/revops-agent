# RevOps agent

## What it is
The agent that answers revenue questions from gold and the context documents, read-only. It routes each question, loads the context it needs, queries gold through four tools and states the definition it used. It never writes.

## Where it runs
Locally and in tests. It has never answered with a real model. Code in `agent/`, directives in `agent/directives/`, skills in `agent/skills/`.

## How to run it
`python agent/agent.py --plan "question"` shows the route with no model. `--ask` needs `ANTHROPIC_API_KEY`.

## Rules
`agent/directives/AGENT.md` and the reading order there; `agent-security`; `writeback-rules`.

## Owner
RevOps lead.

## Status
Built and tested with a scripted model; not run for real (2026-10-31).
