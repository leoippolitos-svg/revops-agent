---
name: medallion-modeling
description: Adds or changes dbt models in the bronze, silver and gold layers following the repo's naming, testing and catalog rules. Use when the user asks to "add a model", "create a gold table", "new metric table", "clean this source" or change the pipeline.
---

# Medallion modeling

Standard: `docs/standards/data-modeling.md`.

## Steps

1. **Pick the layer.** New source → bronze ingestion, never hand-written. Cleaning or typing → silver. Business grain or metric → gold.
2. **Name it** `<entity>_<grain>` in snake_case, singular entity, inside the right schema.
3. **Write the SQL.** Gold reads from silver only; silver reads from bronze only. No layer skipping.
4. **Declare the primary key** and add `unique` and `not_null` tests.
5. **Describe the model and every column** in `schema.yml`. This is the catalog.
6. **Check the concept**: if the model introduces a business concept, load `context-docs` and document it.
7. **Run** `dbt build` for the model and its children.
8. Open a `data` PR with `open-pr`.

## Example

Request: "monthly conversion by funnel stage".
Model: `gold.funnel_stage_monthly`, key `(month, stage)`, built from `silver.deal_stage_history`, with descriptions, tests, and an annotation in `context/concepts/funnel-stages.md`.

## Troubleshooting

- **Duplicates in silver**: deduplicate on the source id keeping the latest `_loaded_at`.
- **Numbers differ from a context doc**: the doc wins. Fix the SQL or open a `context` PR if the doc is wrong.
