---
name: writeback-request
description: "Handles a request to change data by explaining which authorised automation or person can do it, under the write-back rules, without the agent writing anything. Use when someone asks the agent to update, set, assign, merge, delete or fix a record."
---

# Write-back request

## Steps

1. The agent never writes. Say so first, in one sentence.
2. Look the field up in `writeback-rules`. If an automation is authorised for it, name the automation and its trigger.
3. If the field is not listed, it is forbidden for every automation; a person changes it by hand, and a recurring need is a proposal for a new authorization with a decision record.
4. For a sensitive field (an amount, a status that affects billing), the path is a proposal approved item by item, never a bulk change.
5. Give the exact step (system, screen, field) and how to confirm it.

## Example

"Merge these two companies." "Merges are never automatic. They are in the weekly duplicate review queue; a person approves the group and merges it in the CRM by hand."

## Troubleshooting

- **The request is phrased as a question** ("can you set..."): it is still a write; answer with the path.
