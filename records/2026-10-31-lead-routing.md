---
date: 2026-10-31
type: automation
pr: "#40"
author: Leonardo Ippolito
---

# The lead-routing automation

## What was done
Built `automations/lead-routing/route.py` from its spec: it reads lead events and `gold.owner_workload` and writes one line per lead to `observability/logs/lead-routing-<date>.md`, which is the simulated CRM write (ADR-0010). Added 27 tests, marked the spec built and ticked its checklist.

## Why
The rule was written in the context document `lead-routing` and the spec, but nothing applied it.

## Result or decision
- The rules are read from the context document on every run: the capacity limits and the segment-to-team map are parsed from its sentences, so a change there changes the behaviour with no code change. If the document stops saying them in the expected words, the run stops with an error instead of guessing. A test proves a changed limit takes effect.
- Order of rules: no company or segment, then not routed; account continuity; then fewest open deals with the lowest owner id on a tie. A batch adds each assignment to the owner's count as it goes.
- Dry run is the default. `--write` writes the log, and a second run replaces each lead's line, so it adds nothing. A missing or empty table, a bad event or a repeated lead id stops the run with exit code 1 and writes nothing.
- **A conflict between two documents, decided in the safer direction.** The context document says account continuity is not overridden by capacity. The spec's "Must never" says never assign a lead to an owner at the limit. The automation follows the spec: a lead whose account owner is at the limit is listed for a person, not given to that owner and not handed to someone else. The owner should decide which text is canonical; until then the automation does the more cautious thing.
- Not proven: it has not run against the real `gold.owner_workload`, only against hand-made tables, and no real CRM exists.

## Rules and context changed
None. The conflict above is recorded here and as a gotcha in the context document, not resolved.

## Follow-ups
Decide the continuity-versus-capacity conflict. Then the closed-won-provisioning and funnel-review automations.
