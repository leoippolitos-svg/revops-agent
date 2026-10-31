# ADR-0020: Slack alerts are built by code, one thread per item, and simulated until a webhook exists

- Status: accepted
- Date: 2026-10-31

## Context
The reference design sent every job result and every failure to an alerts channel, with the text assembled by code, and kept one Slack thread per problem so a reader saw its whole history in one place. This repository only wrote reports to a log folder, and the Slack connector was documented, never built.

## Decision
- `observability/notify.py` builds each message from a fixed template, never with a model, and keeps one thread per catalog item.
- It writes through the shared write controls under the name `slack-alerts`: dry run by default, a kill switch (`SLACK_ALERTS_ENABLED`), a cap of 30 per run, and "needs review" when a send fails.
- The channel is simulated by `observability/logs/slack-<date>.md`. A real post happens only when the webhook secret `SLACK_WEBHOOK_URL` is also set, and only to `hooks.slack.com`.
- The run catalog collector and the weekly audit call it.

## Alternatives considered
- A bot token with the full Slack API: threads by message timestamp, but a broader credential than one channel needs.
- Let the agent write the alert: a model's wording can soften or invent; an alert must say exactly what the data says.

## Consequences
- Turning alerts on is two deliberate steps (the variable and the secret), and off is one variable.
- Nothing here has posted to Slack; the thread id in the simulation is a local name, not a Slack timestamp.
