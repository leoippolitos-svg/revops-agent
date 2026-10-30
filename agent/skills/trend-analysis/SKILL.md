---
name: trend-analysis
description: Describes how a metric has moved over time, with size, direction and a fair comparison, without over-reading noise. Use when someone asks how a metric has changed, whether MRR, customers, MQLs or funnel volume is going up or down, how this year compares with last, or for a monthly trend.
---

# Trend analysis

A trend is a comparison. Make the comparison fair before describing it.

## Steps

1. Read the context document for the metric. Use its definition and its time rule (which month a record belongs to).
2. Pick the monthly gold table for the metric and read the months asked. Gold months start on the first day.
3. Leave out the month in progress, or label it as partial. It stops at the newest export date and is not comparable with a full month.
4. Describe the movement in three parts: direction, size in absolute terms and as a percentage, and the period it covers. Quote the first and last values.
5. For MRR, check that starting plus new minus churned equals ending in every month. If it does not, say so before describing anything.
6. For the funnel, treat a missing stage-month row as zero. Compare entries to a stage with entries to the same stage, never with deals currently in it.
7. Say how much history there is. With fewer than six full months, do not call a pattern a season or a trend; call it a movement.
8. If one month explains most of the change, name it and say what is known about it. Do not invent a cause. If a cause is asked, offer the `funnel-diagnosis` skill.
9. Check `search_records` for earlier analysis of the same metric and say whether this agrees.
10. Answer with the movement first, then the definition, the table read, the data date and the caveats.

## Example

Illustrative figures. Question: "How has MRR moved this year?"
Answer: "Ending MRR grew from 410,000 to 468,000 USD between January and September, up 14%, with growth in every month except May. Definition: monthly recurring revenue as in the MRR document. Table: the monthly MRR gold table. October is excluded because it is partial."

## Troubleshooting

- **One month is far from the others**: check for a data fault, such as the load date, before treating it as real.
- **The comparison year has less data**: compare only the months both have.
- **Counts are very small**: say the sample is too small to call a direction.
