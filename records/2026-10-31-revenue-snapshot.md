---
date: 2026-10-31
type: app
pr: "#39"
author: Leonardo Ippolito
---

# The revenue snapshot app

## What was done
Built `apps/revenue-snapshot/snapshot.py` from its spec: it writes one static HTML page with MRR, customers, funnel and MQLs, each with the one-sentence definition from its context document. Added 17 tests, marked the spec as built and ticked its security checklist with how each item was checked.

## Why
The spec existed and `check_apps.py` validated it, but there was no app, so leaders' four Monday questions still had four sources.

## Result or decision
- The app is a generator, not a server: the output is a file with no form, no input and no script, so there is nothing for a visitor to send. The four queries are fixed text and run through `query_gold`, so the page can only read gold.
- The newest month is labelled partial and kept out of the headline and the funnel, which use the month before. Sales' MQL count is shown only as "Sales agrees" or "Sales counts differently", never as a number or in a sum. An empty table says "no data for this period".
- Failure follows the spec: a missing or unreadable gold gives a banner and no data, never a path or a stack trace; data older than two days gets a banner and still shows the last data.
- No dependency was added. Freshness is read from the lakehouse file's modified time, because gold has no load date; that is a stand-in, not an export date.
- Not proven: it was rendered once against the local lakehouse, but never opened in a browser, never hosted and never printed, so the phone layout and the one-sheet print are untested.

## Rules and context changed
None.

## Follow-ups
Open it in a browser and print it once. The three automations.
