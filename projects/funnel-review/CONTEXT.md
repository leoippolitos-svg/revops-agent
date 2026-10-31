# Funnel review: context

## Summary
The evidence half is built and tested on hand-made tables. The thresholds and owner teams are assumptions the owner accepted as they are. The agent half has never run.

## Session history

- **Digest, date:** 2026-10-31
- **Context:** the spec asked for a weekly review that names the constraint stage.
- **What was done:** built `review.py`: reads four gold tables read-only, compares the latest three mature cohorts with the three before, writes a report with a hand-off to the diagnosis skill.
- **Result:** a constraint is named only for a conversion drop of 5 points or more weighted by volume, or time in stage up 50% and 3 days; otherwise "no stage changed beyond its normal range".
- **Decision:** the owner accepted those thresholds and the owner team per stage as they are ("beleza"); recorded in `memory/decisions/funnel-review-thresholds.md`.
- **Open items:** confirm the thresholds with real data; run the agent half once a model exists; schedule it once data is fresh.
- **Where the detail is:** `records/2026-10-31-funnel-review.md`, PR #42.
- **Catalog:** not scheduled, so no card yet.
