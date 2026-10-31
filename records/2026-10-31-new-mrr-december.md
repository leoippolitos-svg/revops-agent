---
date: 2026-10-31
type: analysis
pr: "#47"
author: Leonardo Ippolito
---

# Analysis: why new MRR fell in December

## What was done
Added the first finished analysis, `analyses/2026-01-new-mrr-december/`: a query file, a small runner that opens the lakehouse read-only, the saved output and a `result.md` in the standard shape.

## Why
The `analyses/` folder only had its README. A reader of the portfolio could not see the repository doing the one thing it exists for: answering a revenue question with a definition, a data check and a stated limit.

## Result or decision
- New MRR fell 36% in December because 3 deals were won instead of 6. The revenue equals the yearly value won divided by 12, and the average deal was bigger, not smaller.
- Entries into negotiation dipped in November and recovered in December, so the evidence does not say "slowdown". Entries into proposal fell and are the thing to watch.
- Data causes were checked first: the data is current and the flags are too small to matter.
- The analysis lists what would change the conclusion: January or February with 3 or fewer wins and low negotiation entries.
- The data is fictional and the counts are small, which the result says. No earlier record covered December, so nothing is confirmed or changed.

## Rules and context changed
none

## Follow-ups
A second analysis with a different shape, for example a data-discrepancy case between Marketing's and Sales' MQL counts, would show the other skill.
