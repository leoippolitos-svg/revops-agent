---
date: 2026-10-30
type: data
pr: "#24"
author: Leonardo Ippolito
---

# Gold data-quality snapshot

## What was done
Added `gold.data_quality_snapshot`, one row with the number of records carrying each data-quality flag as of the newest export: possible duplicate companies, deals without a company, subscriptions without a deal, and closed won deals with no subscription, each next to its total. Described every column in the dbt `schema.yml`, regenerated `docs/catalog.md`, and added a rule to `cross-cutting-rules` pointing at the table. One new test compares the counts with the silver flags.

## Why
The flags live in silver, and the agent reads gold only. Without this table, "are there duplicate companies?" could not be answered by the agent, and a weekly audit would have had to read silver.

## Result or decision
- The table exposes counts only. The flagged records stay in silver, so the layer boundary is kept.
- `closed_won_without_subscription` includes deals won in the last two weeks, because a subscription starts within two weeks of the win. The column description and the context document both say so, so a small number is not read as a fault.
- The table has one row and the date as its key, so it answers "now" and not "how did this change". Trends of the flags would need a monthly version.

## Rules and context changed
- `context/concepts/cross-cutting-rules.md`: where to read the flag counts, and the two-week caveat. `last_reviewed` set to 2026-10-30.

## Follow-ups
The weekly audit as an automation that reads this table.
