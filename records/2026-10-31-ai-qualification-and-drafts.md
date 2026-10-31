---
date: 2026-10-31
type: automation
pr: "#65"
author: Leonardo Ippolito
---

# Site qualification and prospecting drafts, with AI kept under code

## What was done
- `automations/_lib/ai_step.py`: the one way an automation calls a model. The prompt is a file in the repository and its hash goes with every run; the reply must be one JSON object, validated by the caller; tokens (with cache) and cost are logged per run in `observability/logs/ai-steps.jsonl` with no input text; without a key a scripted client plays the model and the log says "demo".
- `automations/site-qualification/`: removes contact details from a company's website text, asks the fast model for a fixed qualification (fit, technicians, services, quotes, summary), rejects any service off the allowed list and any quote not found word for word, and writes only a validated result (simulated, behind its kill switch).
- `automations/prospecting-drafts/`: only arguments whose evidence was found reach the model, weak-fit leads get no draft and no call, and a draft with a price, discount, guarantee, competitor, link or new number is rejected. Drafts go to a file for the SDR; nothing is sent.
- `tools/check_prompts.py` (in CI): every prompt's hash must be recorded in its spec. A rule document `prospecting` holds the services, arguments and forbidden claims; a write-back authorization for the qualification field; catalog cards; example inputs; 13 tests. Both specs explain the problem, why, projected gains, diagram, where AI enters, tokens and cost, and monitoring.
- The main README describes the eleven automations and the AI steps.

## Why
These are the reference design's website qualification and personalised message flows, rebuilt as code under ADR-0024. Its own lessons are built in: guardrails are structural, not prompt instructions; the repository's prompt is the one that runs, checked by hash; no fabricated signals.

## Result or decision
- In demo mode, the example field-service company qualifies as strong with three real quotes, the design studio as weak, and only the strong lead gets a draft, built on two evidence-backed arguments.
- No real model was called; cost is null until the price table is filled.

## Rules and context changed
New rule document `prospecting`; `writeback-rules` gains `site-qualification`; the `anthropic` connector lists the two automations.

## Follow-ups
Run both with a real key and compare drafts with generic messages, in `BACKLOG.md`.
