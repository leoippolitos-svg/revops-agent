---
date: 2026-10-31
type: automation
pr: "#44"
author: Leonardo Ippolito
---

# Lead routing: continuity may pass the limit by 5%

## What was done
Resolved the open question from the lead-routing record. The owner decided that account continuity stays first but may not take an owner more than about 5% over the capacity limit. The context document now says so, the automation reads the percentage from it, and the spec's "Must never" names the exception.

## Why
The context document and the spec disagreed: one let continuity override capacity, the other forbade assigning to an owner at the limit. The automation had been holding such leads for a person.

## Result or decision
- The rule is in `context/concepts/lead-routing.md`: the account owner may go at most 5% over the limit, rounded down, and past that the lead is listed for a person.
- The ceiling is `limit * (100 + 5) // 100` in whole deals: 31 for the sales team (limit 30) and 8 for the enterprise team (limit 8), so enterprise gets no tolerance. The code reads the 5 from the document, and a test shows that changing it changes the ceiling.
- **My reading of "5% or so":** 5% over the limit, counted in whole deals and rounded down. If the owner meant 5% of the owner's own open deals, or rounding up, this one line changes.
- A lead given within the tolerance says so in the log's rule column. A second lead for the same owner after it reaches the ceiling is listed for a person.

## Rules and context changed
`context/concepts/lead-routing.md`: the continuity rule, and the gotcha about the open question replaced by one saying what 5% means for each team. `automations/lead-routing/SPEC.md`: the exception in "Must never".

## Follow-ups
None for this rule. The funnel-review thresholds and owner teams are still waiting on the owner.
