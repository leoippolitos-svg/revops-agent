# ADR-0019: A fifth read-only tool, get_map, for closed maps

- Status: accepted
- Date: 2026-10-31

## Context
The agent may not show ids, and many questions name a person, a team or a stage ("Dana's deals", "deals stuck in proposal"). Resolving those through retrieval is probabilistic, and resolving them by querying silver breaks the gold-only rule. The reference design had a `get_mapa` tool for this: the model picks a key from a closed list and the tool reads a fixed source.

## Decision
- Add `get_map(key)`, read-only. Keys: `owners` and `funnel_stages` (fixed SELECTs over gold through `query_gold`), and `teams`, `segments`, `pipelines`, `apps` (one section of a context document, looked up by id in the index).
- Add the gold model `owner_directory` (owner id, full name, team, no contact detail) so names come from gold.
- Offer the tool to `metric_lookup`, `funnel_diagnosis` and `report_request`, the intents that name people or stages.

## Alternatives considered
- Let the model query `gold.owner_workload` and guess names: the table has no names by design.
- A free-text path or query argument: that would turn the map into arbitrary reading of the repository or the lakehouse.
- Put names in `owner_workload`: mixes a workload fact with a directory, and every routing query would carry names it does not need.

## Consequences
- Five tools instead of four; a new key is a code change reviewed in a pull request, never a model choice.
- The owner directory holds names of (fictional) people, which `agent-security` allows; contact details stay out of gold.
