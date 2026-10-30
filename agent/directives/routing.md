# Routing

The router classifies each question into one intent. Each intent sets the tools, the model tier and the skill to use.

| Intent | Example question | Tools | Model tier | Skill |
|---|---|---|---|---|
| `metric_lookup` | "How many MQLs did we get in September?" | search_context, query_gold | fast | — |
| `trend_analysis` | "How has MRR moved this year?" | search_context, query_gold | standard | trend-analysis |
| `funnel_diagnosis` | "Why did conversion drop?" | search_context, query_gold, search_records | standard | funnel-diagnosis |
| `definition_question` | "What counts as an active customer?" | search_context | fast | — |
| `data_quality` | "Why don't these two numbers match?" | search_context, query_gold, get_catalog | standard | data-discrepancy |
| `past_work_lookup` | "Did we analyze churn in enterprise before?" | search_records | fast | — |
| `report_request` | "Build me a pipeline review for Monday" | search_context, query_gold | standard | html-report |
| `out_of_scope` | "Update this deal to closed won" | none | fast | — |

## Model tiers

- **fast**: short classification and lookups.
- **standard**: multi-step reasoning and diagnoses.

## Ambiguity

If two intents fit, pick the one that needs fewer tools and say which assumption you made. If none fits and the question is about revenue, use `metric_lookup` and say that you read it as a lookup. If it is not about revenue, or asks you to change or send something, use `out_of_scope`. The rules are in `agent/router.py`.
