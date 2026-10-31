# Routing

The router classifies each question into one intent. Each intent sets the tools, the model tier and the skill to use.

| Intent | Example question | Tools | Model tier | Skill |
|---|---|---|---|---|
| `metric_lookup` | "How many MQLs did we get in September?" | search_context, query_gold, get_map | fast | — |
| `trend_analysis` | "How has MRR moved this year?" | search_context, query_gold | standard | trend-analysis |
| `funnel_diagnosis` | "Why did conversion drop?" | search_context, query_gold, search_records, get_map | standard | funnel-diagnosis |
| `definition_question` | "What counts as an active customer?" | search_context | fast | — |
| `data_quality` | "Why don't these two numbers match?" | search_context, query_gold, get_catalog | standard | data-discrepancy |
| `past_work_lookup` | "Did we analyze churn in enterprise before?" | search_records | fast | — |
| `report_request` | "Build me a pipeline review for Monday" | search_context, query_gold, get_map | standard | html-report |
| `out_of_scope` | "Update this deal to closed won" | none | fast | — |

## Category profiles

What each intent loads besides the question. **Fixed documents** are read by exact id on every question of that intent, because retrieval is probabilistic and what an answer needs cannot depend on the luck of the top results. **Context chunks** is how many retrieved sections are added after them: an intent with many fixed documents needs fewer. `agent-security`, `AGENT.md` and `fallback.md` are in every prompt and are not listed.

| Intent | Fixed documents | Context chunks |
|---|---|---|
| `metric_lookup` | company, entities, data-map | 3 |
| `trend_analysis` | company, okrs, data-map | 4 |
| `funnel_diagnosis` | funnel-stages, metrics-sales, crm-map, data-map | 3 |
| `definition_question` | company | 5 |
| `data_quality` | cross-cutting-rules, metrics-revops, data-map | 3 |
| `past_work_lookup` | — | 2 |
| `report_request` | company, okrs, data-map | 4 |
| `out_of_scope` | — | 0 |

Fewer tools give better answers: offering a tool the intent does not need invites the model to look in the wrong place, so each intent lists only its own.

## How a question is classified

In this order, and the step that decided is logged as `via`:

1. **model**: when a classifier is configured, the cheapest model answers with one intent id and nothing else. An id that is not in the table above is ignored.
2. **rules**: the patterns in `agent/router.py`.
3. **default**: `metric_lookup`, on the **standard** tier, not the fast one. A question no rule understands is the one that least deserves the weakest model.

Classification never fails a question: each step falls to the next.

## Model tiers

- **fast**: short classification and lookups.
- **standard**: multi-step reasoning and diagnoses.

## Ambiguity

If two intents fit, pick the one that needs fewer tools and say which assumption you made. If none fits and the question is about revenue, use `metric_lookup` and say that you read it as a lookup. If it is not about revenue, or asks you to change or send something, use `out_of_scope`. The rules are in `agent/router.py`.
