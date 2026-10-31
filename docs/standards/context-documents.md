# Context documents

A context document teaches the agent what the business **means**. It is written once and delivered every time the agent touches the data.

## Catalog vs context document

| | Catalog | Context document |
|---|---|---|
| Answers | What is this table or column? | What does this concept mean for the business? |
| Example | `gold.subscription_monthly.status`: subscription status at month end | "Active customer": a paid subscription with at least one confirmed payment, excluding test accounts |
| Lives in | dbt `schema.yml` descriptions | `context/concepts/*.md` |
| Granularity | One entry per table and column | One document per concept |

Do not describe tables or columns in a context document. That belongs in the catalog.

## What goes in

- The definition of a metric or concept, in plain language.
- Rules that cross several tables.
- Gotchas that affect any analysis: exclusions, test accounts, soft deletes, currencies, time zones.
- Where definitions differ between teams, and which one is canonical.
- Annotations for every table and column the prose mentions.

## What stays out

- Implementation details. Schemas change, definitions do not. Describe what the metric means, not the SQL.
- Several concepts in one document. Split them and link.
- Repeated rules. Link to the document that owns the rule instead of copying it.

## Annotations

Annotations link the prose to real resources so the agent gets business and technical context together.

- Table: `[[gold.subscription_monthly]]`
- Column: `[[gold.subscription_monthly.status]]`
- Another concept: `[[concept:active-customer]]`

CI checks that every annotation resolves to an existing model, column or concept. Renaming a column without updating the context fails the PR.

## Structure

Start from [`context/_template.md`](../../context/_template.md).

1. **Frontmatter**: `id`, `title`, `owner_team`, `status` (`draft` | `canonical` | `deprecated`), `last_reviewed`, `related`.
2. **Definition**: three sentences maximum. If you cannot define it in three, it is two concepts.
3. **Rules**: what is included and excluded, with annotations.
4. **Gotchas**: what makes a naive query wrong.
5. **Team differences** (if any): how other teams use the word and which version is canonical.
6. **Examples**: one or two worked examples with expected results.

## Kinds of documents

Concepts are one kind. The agent also needs to know the company, each area, how metrics are computed, how the CRM is organised and which rules hold. Those live next to the concepts, one folder per kind, and are listed under `documents` in `context/index.yaml` with their `kind`:

| Folder | Kind | Holds | Required sections after "Purpose" |
|---|---|---|---|
| `company/` | `company`, `okrs`, `entities` | what Fernway sells, the goals of the cycle, who is who | set per kind in `tools/check_context.py` |
| `areas/` | `area` | one per area: mission, people, objectives, KPIs, CRM objects, benchmarks, frequent questions, anti-confusions | Mission … Anti-confusions |
| `metrics/` | `metrics` | one per area: formula, source and status of every metric | Metrics, Window and grain, Internal benchmark, Interpretation notes |
| `crm/` | `crm-map`, `data-map` | pipelines, stages, fields and owners; how to query gold | include a model query |
| `reports/` | `report`, `benchmark` | how each number of a report is computed; external references | Numbers and how they are computed, Changelog |
| `rules/` | `rule`, `inventory` | rules that cross areas (write-back, ICP) and inventories (apps) | Rules, Owner and approvers |

Rules for every non-concept document:

- It opens with **Purpose**: what it is for, who reads it and when, what does not belong in it, who owns it and when it is updated. A reader decides in one paragraph whether to keep reading.
- It links to concepts instead of repeating them: an area or metrics document points at `[[concept:mql]]`, never redefines it. Documents link to each other with `[[doc:id]]`.
- A metric whose data is not in gold is listed with the status "not in gold yet". The agent then says it is a data task; it never reads silver to answer.
- Only `crm-map` and `data-map` documents may hold a code block, for the model query the agent starts from. The biggest quality gain in the reference design came from telling the agent which table to query and showing one working query.

## When to create or update

- A new gold model introduces a concept that is not documented yet.
- A human corrects an agent answer because of a definition. The correction becomes a `context` PR.
- A process change alters a rule (for example, a new funnel stage).

## Style

Write as if explaining to an analyst on their first week. Short sentences, concrete examples, no jargon without a definition.
