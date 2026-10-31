---
name: refinement
description: "Turns a request into a short spec before any code: problem, users, inputs, rules, effects, what it must never do, and how it will be verified. Use when the user asks for something new that runs, writes or is used by others, says build or create a feature, or the request is vague."
---

# Refinement: spec before code

## Steps

1. Write the problem in two sentences and who it is for.
2. List inputs (gold tables, events), the rules (linked context documents, never copied) and the effects.
3. Write what it must never do: writes, data it must not read, actions it must not take.
4. Say how it will be verified: tests, the eval, a manual check, the reviewer agent.
5. List open questions for the owner; ask them before building, all at once.
6. Commit the spec (an automation or app spec, or a plan in the project's CONTEXT.md) before the first line of code.

## Example

"Alert me when a big deal stalls." Spec: trigger weekly, input open deals from gold, rule "proposal for more than the median plus 14 days", effect one Slack alert through the notifier, must never write to the CRM, verified by a test on hand-built tables. Open question: what counts as big.

## Troubleshooting

- **The owner wants it now**: the spec takes minutes and saves the rebuild.
