---
name: score-deals
description: "Ranks open deals by how likely they are to close, from stage, age in stage and size, with the reason for each score. Use when someone asks which deals to focus on, which deals are likely to close this month, or which pipeline is stuck."
---

# Score deals

## Steps

1. Read `funnel-stages` and `metrics-sales`. Resolve owner names with the map tool.
2. Use open deals only. For each: current stage, days in the stage, amount.
3. Score with a rule written in the answer, not a black box: later stage scores higher; days in stage above the median for that stage scores lower; very large deals are flagged for review, not scored up.
4. Show the top deals with the reason for each score in words ("negotiation, 12 days, under the median").
5. Never present the score as a probability; it is an order of attention.
6. End with cuts: by owner, by segment, stuck deals only.

## Example

"Which deals should we focus on?" Ten deals in negotiation and proposal, ordered by stage and time in stage, each with its owner's name and the reason.

## Troubleshooting

- **Days in stage look wrong**: some deals have stage dates out of order; they are counted apart in the time-in-stage table.
