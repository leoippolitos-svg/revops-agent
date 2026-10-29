# Context

Business concepts, one per document, in `concepts/`. Start from `_template.md`, register each document in `index.yaml`, and follow [docs/standards/context-documents.md](../docs/standards/context-documents.md).

Table and column descriptions are not here: they live in the dbt `schema.yml` files (the catalog).

## The five concepts

| Document | Owner | What it settles |
|---|---|---|
| [active-customer](concepts/active-customer.md) | Customer Success | Who counts as a paying customer, per company |
| [mrr](concepts/mrr.md) | RevOps | Monthly recurring revenue, new and churned |
| [funnel-stages](concepts/funnel-stages.md) | Sales | The stages a deal moves through, with entry and exit criteria |
| [mql](concepts/mql.md) | Marketing | The qualified lead, and whose flag is canonical |
| [cross-cutting-rules](concepts/cross-cutting-rules.md) | RevOps | Currency, dates, internal accounts, data-quality flags, sources of truth |

`python tools/check_context.py` keeps them honest: every annotation must point at a real model, column or concept, and every document must follow the template (five sections, a definition of at most three sentences, no SQL).
