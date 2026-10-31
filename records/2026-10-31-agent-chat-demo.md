---
date: 2026-10-31
type: app
pr: "#62"
author: Leonardo Ippolito
---

# Agent chat: a local demo of the agent, no key needed

## What was done
- `apps/agent-chat/`: a server on the standard library that listens on 127.0.0.1 only, a page, and a scripted model (`demo_model.py`) with the same method as the real adapter. Each answer comes with its trace: intent and the cascade step that chose it, tier and budget, tools offered, documents always loaded, the four prompt blocks, tools called and model calls.
- In demo mode the router, the profile, the prompt blocks, the budget, the tool guards and the refusal of writes are the real agent, and the tools run on the local lakehouse; only the tool choice and the wording are scripted, and every answer says no model was called.
- Guards: Origin check, JSON with one field of at most 500 characters, a strict Content-Security-Policy with no third-party script, a page built with text only, no question in any log. ADR-0023; ADR-0022 now covers only hosting.
- The app README maps the page to the mechanisms of the original and compares them with current practice for data-analyst agents, with sources. Spec, catalog card, inventory row, 13 tests, and a screenshot in the main README.

## Why
The owner wanted a way to show, with no key, that the agent works the way the original did, and to have it documented. The original's chat had ported its quality mechanisms from a data agent built by an engineering team; that code is not in the dossier (only references to it), and it belongs to another team, so this app recreates the mechanisms, not its files.

## Result or decision
- The app runs locally and was opened in a browser: the example question routes by rule to the fast tier, loads company, entities and the data map, calls `query_gold` and shows the real rows.
- It has never answered with a real model and is not hosted.

## Rules and context changed
`context/rules/apps.md` (a new row). No business rule changed.

## Follow-ups
Hosting for a team with sign-in, and a real-model run, in `BACKLOG.md`.
