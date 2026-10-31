---
name: cross-source-analysis
description: "Answers a question that needs two sources, such as CRM deals and billing subscriptions, by matching on an explicit id and stating the coverage of the match. Use when a question crosses sales and revenue, deals and customers, or marketing and pipeline."
---

# Cross-source analysis

## Steps

1. Name both sources and the source of truth for the topic (`cross-cutting-rules`).
2. Find a gold table that already joins them (for deals and subscriptions, `deal_subscription_reconciliation`). Never join gold to silver.
3. Match only on an explicit id. State how many records matched and how many did not.
4. Report the unmatched records as a list, classified; an aggregate without its ids cannot be acted on.
5. When the sources disagree, the source of truth wins, and the answer says the other differs.

## Example

"Do won deals match revenue?" "35 of 39 records match; one won deal has no subscription after 88 days, two are within the two-week wait, and one subscription has no deal."

## Troubleshooting

- **The match rate looks too good**: check that the join did not multiply rows; count before and after.
