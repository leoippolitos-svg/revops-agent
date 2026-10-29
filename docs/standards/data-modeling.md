# Data modeling and naming

## Layers

Layers are separated **by schema**, never by prefix. Mixing both is the failure to avoid.

| Layer | Schema | Purpose | Written by |
|---|---|---|---|
| Bronze | `bronze` | Raw mirror of each source, append-only | Ingestion only |
| Silver | `silver` | Cleaned, typed, deduplicated, one row per entity | dbt |
| Gold | `gold` | Business grain, joins across sources, metrics ready to use | dbt |

The agent and the MCP server read **gold only**.

## Naming

- `snake_case` everywhere. No camelCase, spaces or accents.
- Entities are singular: `deal`, `company`, `subscription`.
- Bronze mirrors the source: `bronze.<source>_<object>`, e.g. `bronze.crm_deals`.
- Silver is the clean entity: `silver.deal`, `silver.deal_stage_history`.
- Gold states entity and grain: `gold.<entity>_<grain>`, e.g. `gold.funnel_stage_monthly`, `gold.customer_channel_monthly`.
- No cryptic names: no `tbl1`, `base_v2`, `final_data`.

## Required columns

- Bronze: `_loaded_at`, `_source`, `_batch_id`.
- Silver and gold: a declared primary key, tested `unique` and `not_null`.

## Catalog

Every model and every column has a description in its dbt `schema.yml`. An undocumented gold model fails CI. Descriptions feed the catalog the agent reads.

## Idempotency

Running the pipeline twice on the same input produces the same output. Gold models are rebuilt from silver; nothing is updated in place.
