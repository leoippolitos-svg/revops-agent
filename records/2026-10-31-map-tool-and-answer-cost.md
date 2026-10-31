---
date: 2026-10-31
type: app
pr: "#53"
author: Leonardo Ippolito
---

# Agent: the get_map tool and the cost of each answer

## What was done
- New read-only tool `get_map(key)` with six closed keys: `owners` and `funnel_stages` from fixed gold queries, and `teams`, `segments`, `pipelines` and `apps` from one section of a context document. Any other key is refused. Offered to lookups, funnel diagnoses and reports. ADR-0019.
- New gold model `owner_directory` (owner id, full name, team, no contact detail), with its catalog entry and a dbt test; `entities` and `crm-map` now resolve names through it.
- Cost per answer: tokens per model including cache writes and reads are summed across every call of an answer, the classifier included, and converted with a price table in `agent/tools/README.md`. The table is empty on purpose, so the cost is logged as `null`, never zero.
- `run_agent(use_classifier=True)` lets the fast model pick the intent first; a reply that is not a known id falls back to the rules. The log records `via`, cache tokens, whether the classifier ran and `cost_usd`.

## Why
In the original, every "by person" question needed an owner map, because the agent may not show ids, and a closed map made that deterministic. Its cost log counted cache tokens and the classifier, and used null for a model without a price, so a new model could not look free while it spent.

## Result or decision
- Prices are not written from memory: the repository has never called the API. A person fills the table from the provider's page.
- 15 tests added (map keys and refusals, cost arithmetic, classifier routing and fallback, the directory model).

## Rules and context changed
`agent/directives/routing.md` (tools of three intents); `entities` and `crm-map` point at `gold.owner_directory`.

## Follow-ups
Automation controls library and the write-back check, then the run catalog.
