---
name: recommend-automation
description: "Spots a recurring manual question or task that should become an automation, and drafts the spec outline under the automation standard. Use when someone asks the same question every week, says a task is repetitive, or asks what could be automated."
---

# Recommend an automation

## Steps

1. Confirm it recurs: the same question or task at least monthly, with the same inputs.
2. Check the run catalog and `automations/` for something that already does it.
3. Draft the outline in the shape of an automation spec: problem, trigger, inputs (gold only), rules (linked context documents), effects, failure behaviour, must never, dry run.
4. If it writes anywhere, say it needs a write-back authorization and a decision record; if it compares sources, say it follows the audit standard.
5. Hand it to a person as a proposal; the agent never creates or runs automations.

## Example

"Every Monday someone checks deals won without a subscription." "The reconciliation audit already does it weekly; see its card in the run catalog."

## Troubleshooting

- **The task needs judgment each time**: it is a skill, not an automation (ADR-0009).
