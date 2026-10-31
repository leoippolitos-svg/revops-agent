---
date: 2026-10-31
type: app
pr: "#37"
author: Leonardo Ippolito
---

# The model adapter, structure only

## What was done
Built `agent/model_client.py`: `AnthropicClient`, which turns the loop's messages and tool specs into a Messages API request and the reply back into text, a tool call and token usage. Added `--ask` to `agent/agent.py`, 15 tests with a fake transport, ADR-0016 and the README updates.

## Why
The owner wanted the structure of a working agent in the repository without spending money or handling a key.

## Result or decision
- No dependency: the request is sent with the standard library (ADR-0016). Only `http_transport` touches the network, and tests replace it.
- The key comes from the `ANTHROPIC_API_KEY` environment variable only, goes only in a header, and is not in the request body or any error. With no key, `--ask` exits with a message before any network use.
- Tested with a fake API: request shape, tool schemas, tool-call ids, text and tool-use replies, API errors cut short, a non-JSON reply, a network failure, and a full loop run through the adapter.
- Not proven: that the live API accepts exactly this request. It has never been called. There are no retries, no streaming and no cost logging.

## Rules and context changed
None. The connector registry entry for `anthropic` gained a note saying it has never been called with a key.

## Follow-ups
Someone with a key runs `--ask` once; then the first scored context A/B, skill-trigger and answer-quality runs.
