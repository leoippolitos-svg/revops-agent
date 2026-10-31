---
name: cohort-analysis
description: "Compares groups of deals or customers that started in the same month, so results are judged on mature cohorts and never on immature ones. Use when someone asks how a cohort performed, compares win rates across months, asks whether recent months convert worse, or wants retention by start month."
---

# Cohort analysis

## Steps

1. Read `funnel-stages` (deals) or `mrr` and `active-customer` (customers) for the cohort rule: which month a record belongs to and when a cohort is mature.
2. Use the cohort table, never entries of one month divided by entries of another (`gold.funnel_conversion_monthly` for deals).
3. Keep only mature cohorts: 90 days past the end of their month for deals. Name the immature ones and say they will move.
4. Check the sample: a cohort under the minimum in `funnel-stages` (20 qualified deals) is listed, not compared.
5. Compare each cohort with the range of the mature ones, not with one cohort; give counts next to every rate.
6. Say what changed in the mix (segment, team) before calling a cohort better or worse.
7. Answer with the comparison first, the definition, the source in plain words, the data date and the caveats.

## Example

"Do recent cohorts win less?" Mature cohorts from May to August won 18% to 69% of what they closed; September has 14 qualified deals, under the minimum, so it is listed but not compared; October to December are immature.

## Troubleshooting

- **A recent cohort looks terrible**: it is immature; its open deals have not closed yet.
- **A rate jumps between two cohorts**: check the counts; one deal moves a small cohort by many points.
