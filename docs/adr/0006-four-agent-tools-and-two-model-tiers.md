# ADR-0006: Four agent tools and two model tiers

- Status: accepted
- Date: 2026-10-30

## Context
The RevOps agent needs data, meaning and history. Many overlapping tools confuse the model and widen what it can break. CLAUDE.md requires an ADR for every new agent tool.

## Decision
The agent has exactly four tools, all read-only: `query_gold` (gold schema only), `search_context`, `get_catalog` and `search_records`. Their contracts are in `agent/tools/README.md`. A router picks one of two model tiers per question: `fast` for lookups and classification, `standard` for multi-step reasoning (see `agent/directives/routing.md`). Model ids live in one place, `agent/tools/README.md`, so a model change is a one-line edit.

## Alternatives considered
- **One generic "run SQL" tool**: simple, but it gives up the context layer and widens the attack surface.
- **One model for everything**: simpler, but pays the strong model's price for definition lookups.

## Consequences
A small, auditable surface, and cost that follows difficulty. Adding a fifth tool needs a new ADR. The contracts are rules in the repo for now; code that implements them comes later and is tested against them.
