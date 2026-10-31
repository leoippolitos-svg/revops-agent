# ADR-0022: The web chat app waits for a host and a key

- Status: accepted
- Date: 2026-10-31

## Context
The original agent had two faces: the agent in the IDE, used by the RevOps team, and a web chat for leaders, with single sign-on, an allowlist at the door, a database role per app, row-level security on conversations, and the cost of every answer stored. This repository recreates the agent, its context, its controls and its operations, but has no host and no model key.

## Decision
Do not build the web chat now. Keep everything it would call ready and tested: the agent loop with its four-block prompt and profiles, the five read-only tools, the cost log, the security policy by role, and the app standard and template. When a host and a key exist, the chat is a new app built from `apps/_template` under the engineering rules 1 to 17, with its own decision record.

## Alternatives considered
- Build the chat without hosting it: a page nobody can open proves nothing about sign-in, the allowlist or row-level security, which are the hard parts.
- Host it on a free tier with a personal key: a public portfolio repository would invite cost and abuse with no allowlist owner.

## Consequences
- The agent is reachable only from the command line (`--plan`, `--ask`) and the MCP server.
- The security rules for sign-in, sessions and row-level security wait for the first app that needs them, as the security standard says.
