---
date: 2026-10-29
type: context
pr: "#12"
author: Leonardo Ippolito
---

# The first five context documents, canonical

## What was done
Finished the five context documents of Phase 2 (`active-customer`, `mrr`, `funnel-stages`, `mql`, `cross-cutting-rules`), settled the decisions the drafts had left open, set all five to `canonical`, and made `tools/check_context.py` enforce the template.

## Why
The agent answers from these documents, so each concept needs one clear definition and one place. Drafts with open questions would have made the agent guess.

## Result or decision
- MQL: Marketing's flag is canonical, because it comes from the same form scoring for every lead and can be audited. Sales' flag is read as agreement, never summed with Marketing's, and disagreements are a signal to tune scoring.
- Funnel: entry and exit criteria written for each of the four open stages and the two closed ones. A deal is "qualified" for the funnel when it leaves qualification. A won deal starts a subscription within two weeks, which matches how the generator builds the data.
- Cross-cutting rules: US dollars, calendar dates with no time zone conversion, "as of" the newest export, internal and test accounts excluded from every metric (none exist in Fernway's data today), the source of truth per topic, and how each data-quality flag is treated.
- The fictional company's rules were invented to fit the template and the data, in the structure of the Nekt context-document guidance credited in the README. Nothing real from any employer is used.
- `check_context.py` now also fails on missing front matter, a missing or empty section, a definition of more than three sentences and any code block. It passes on all five documents and fails on each broken case in 6 new tests (20 in total in `tests/test_checks.py`).

## Rules and context changed
- `context/concepts/cross-cutting-rules.md`: new, canonical.
- `context/concepts/mql.md`, `funnel-stages.md`: decisions made, canonical.
- `context/concepts/active-customer.md`, `mrr.md`: linked to the cross-cutting rules, canonical.
- `context/index.yaml`: all five canonical.

## Follow-ups
A rendered, browsable catalog and the close of Phase 2 (next PR).
