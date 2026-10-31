---
date: 2026-10-31
type: automation
pr: "#70"
author: Leonardo Ippolito
---

# Proposal generator, account review narrative, and the prompt library

## What was done
- `automations/proposal-generator/`: the model extracts facts from a meeting note (technicians, pain points, current tool, decision date, quotes), every one checked against the note; the proposal is assembled by code from those facts, the plan rule and the deal's amount in gold. Never sent.
- `automations/ebr-narrative/`: a data pack from gold (health, onboarding, subscriptions), prose from the model around it, and any number or date not in the input, any guarantee or any text past the limits rejected.
- The agent chat now titles each thread through a fast-tier step, and the retrieval ingest can add a one-line summary per changed chunk (`--summaries`, display only). Both prompts live in `agent/prompts/`.
- `docs/prompt-library.md` lists every prompt the system sends, who uses it, its answer shape and its hash; `tools/check_prompts.py` now checks the agent's prompts against it too.
- A rule document `proposal-rules`, specs with gains and diagrams, catalog cards, index rows, and 11 tests.

## Why
The dossier's micro-apps included a proposal generator and an account narrative for executive reviews, and its prompt library had the conversation title, the chunk summary and the meeting-field extraction. They show AI applied to RevOps beyond the agent, always kept under code.

## Result or decision
- In demo mode the example meeting note gives a growth-plan proposal for 42 technicians with the deal's recorded amount; the red-band account gets a recovery next step.
- No real model was called.

## Rules and context changed
New rule document `proposal-rules`; the `anthropic` connector lists the new consumers.

## Follow-ups
The full security review pipeline, then the README pass.
