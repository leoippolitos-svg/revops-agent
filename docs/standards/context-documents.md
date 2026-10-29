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

## When to create or update

- A new gold model introduces a concept that is not documented yet.
- A human corrects an agent answer because of a definition. The correction becomes a `context` PR.
- A process change alters a rule (for example, a new funnel stage).

## Style

Write as if explaining to an analyst on their first week. Short sentences, concrete examples, no jargon without a definition.
