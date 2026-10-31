# New MRR fell 36% in December because 3 deals were won instead of 6, and nothing yet says it is a slowdown

**Question:** new MRR fell from $33,741 in November to $21,558 in December. Is that the start of a slowdown?
**Decision it supports:** whether to plan the next quarter on the December pace or on the autumn pace, or to wait one more month before deciding.

## Data as of

2026-01-09, the newest daily export loaded. December is a full month and is compared with full months. January is partial and is left out.

## Evidence

Full output: [output.txt](output.txt). Query: [query.sql](query.sql). To repeat: `python analyses/2026-01-new-mrr-december/run.py`.

- **The drop is a count of deals.** December had 3 closed won deals against 6 in each of October and November. December new MRR ($21,558) equals the yearly value won ($258,700) divided by 12, so the revenue follows the deals one to one.
- **Value per deal went up, not down.** The average yearly value of a won deal was $86,233 in December against $64,233 in November. Fewer deals carried the month, each one bigger.
- **The earlier stage dipped first.** Entries into negotiation fell from 11 in October to 6 in November, and the won deals fell one month later, from 6 to 3. That order is what a lag looks like.
- **December entries into negotiation recovered**: 8, against 6 in November. Entries into proposal fell, from 11 to 8, so the earlier stage is the one to watch.
- **Ending MRR still grew**: $104,508 to $124,132 (+18.8%). December also has the first churn in the data, $1,934, which lowers ending MRR but not new MRR.
- **Mature cohorts do not show a falling win rate.** The cohorts from April to September (the ones old enough to compare) won 18% to 69% of the deals they closed, and the most recent ones are higher, not lower (40%, 69%, 60% for July to September). The October to December cohorts are not mature, so they say nothing yet.
- **A rough size of the swing.** The five months before December averaged 5.2 won deals. If wins behave like independent events at that rate, a month with 3 or fewer happens about one month in four (e^-5.2 × (1 + 5.2 + 13.52 + 23.43) ≈ 0.24). That is a rough check, not a model, and it only says 3 is not unusual.

**Data causes ruled out.** The data is 9 days old at the time of reading, which is current. Of 205 deals, 4 have no company, and of 36 closed won deals, 1 has no subscription. Those flags are too small to move a month by $12,000. No definition changed: new MRR is the value of subscriptions that started in the month, as in the context document.

## Definitions used

- New MRR, MRR and churned MRR: [mrr](../../context/concepts/mrr.md).
- Funnel stages, entering a stage, cohorts, maturity (90 days) and the minimum of 20 qualified deals for a comparison: [funnel-stages](../../context/concepts/funnel-stages.md).
- "As of", flags and sources of truth: [cross-cutting-rules](../../context/concepts/cross-cutting-rules.md).

## Tables read

`gold.mrr_monthly`, `gold.funnel_stage_monthly`, `gold.funnel_conversion_monthly`, `gold.data_quality_snapshot`. Gold only, read-only connection.

## Caveats

- The counts are small. A month moves by one or two deals, so every percentage here is fragile.
- A won deal becomes a subscription up to two weeks later, so new MRR and the won deals of the same month can differ a little. In December they matched exactly.
- Only four of the nine mature cohorts (2025-05 to 2025-08) have the 20 qualified deals the funnel-stages document asks for. The other five are listed, but their win rates are too small a sample to compare.
- The data is fictional and generated, so the finding shows the method, not a real business.
- No loss reason exists in the data, so this analysis cannot say why any deal was lost.
- No earlier record covers December: `records/2026-10-30-gold-funnel-conversion.md` only notes that the 2025-12 cohort is immature. This analysis neither confirms nor changes it.

## What would change this conclusion

- January or February closing with 3 or fewer won deals again, with entries into negotiation also staying low, would make it a slowdown.
- Entries into proposal staying near 8 a month, down from 11, would show the earlier stage is thinning.
- A mature cohort with 20 or more qualified deals and a win rate falling from one cohort to the next.
