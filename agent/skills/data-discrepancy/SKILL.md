---
name: data-discrepancy
description: Explains why two numbers that should match do not, and says which one to use for which purpose. Use when someone asks why two reports disagree, why a count does not match another team's, why a number changed without a business reason, or whether a figure can be trusted.
---

# Data discrepancy

Two numbers that disagree usually answer two different questions. Find the question each one answers before looking for a bug.

## Steps

1. Get both numbers exactly as stated: the value, the metric name, the period, who produced it and when.
2. Read the context document for the metric and `cross-cutting-rules`. Write down the definition each number appears to use.
3. Check the usual causes in this order, and stop at the first one that explains the gap:
   - **Different definitions**: for example a customer counted from a CRM stage versus a paid subscription, or Marketing's MQL flag versus Sales' flag.
   - **Different dates**: the month in progress is partial, and the figures are as of the newest export loaded. Compare like with like.
   - **Source of truth**: when two systems disagree, the source named in `cross-cutting-rules` wins for that topic.
   - **Flagged records**: duplicate companies, deals without a company, subscriptions without a deal. A flag is not a filter, so check whether each side included them.
   - **Grain**: one number counts entries to a stage, the other counts deals currently in it.
4. Reproduce the gap with `query_gold`, reading only gold. If the cause needs rows that gold does not expose, say so and name the check a person with silver access should run. Do not guess.
5. Check `search_records` for an earlier reconciliation of the same pair.
6. Answer in this order:
   - the cause of the gap in one sentence, or "not found" with what was ruled out;
   - a small table: each number, its definition, its source table, its date;
   - which number to use for which decision;
   - the owner team who can correct the source, if it is a data fault.

## Example

Illustrative figures. Question: "Sales says we have 140 customers, Customer Success says 126."
Finding: Sales counts closed-won deals, Customer Success counts paid subscriptions. The 14 difference is deals closed won whose subscription has not started or has ended. For revenue and retention use 126, the billing source of truth; for pipeline conversion use 140. The context document for active customers names both.

## Troubleshooting

- **The gap is small and moves every day**: the periods are not aligned. Align the date first.
- **Both numbers use the same definition and still differ**: a data fault is likely. Report the numbers and tables and hand over to the `fix-failing-data-check` workflow through a person.
- **No context document covers the metric**: follow `fallback.md`: show what the data says and state that no canonical definition exists.
