---
name: escalate-to-human
description: "Says clearly when a question needs a person: a decision, a write, an approval or data the agent cannot reach, and gives the exact next step. Use when someone asks the agent to change data, approve something, decide a policy, or when the answer would need data outside gold."
---

# Escalate to a human

## Steps

1. Name what is needed in one sentence: a decision, a write, an approval or a data source.
2. Say who can do it, by role, from `entities` and `writeback-rules`.
3. Give the exact address of the step: system, screen, field, expected value, and how to confirm it afterwards.
4. If an automation exists for it (lead routing, provisioning), say it is the path and that the agent does not run it.
5. Never do the step partially, and never write a "suggested change" that looks applied.

## Example

"Reassign this lead to Dana." "I cannot change owners. Lead routing assigns owners by the routing rule; a manual change is made by RevOps in the CRM, on the lead's owner field. If the rule picked the wrong owner, that is a change to the `lead-routing` document."

## Troubleshooting

- **The person insists it is urgent**: urgency does not change who may write; give the fastest correct path.
