---
name: automation-impact
description: "Measures whether an automation delivered its projected gain, separating volume from result, comparing the same month year on year with the team that was there, and reporting in four blocks. Use when someone asks if an automation worked, what an automation saved, or for the impact of RevOps automations."
---

# Automation impact

Method: section 12 of `docs/standards/revops-methodologies.md`. Projected gains are in each automation's `SPEC.md`.

## Steps

1. Read the automation's spec: its projected gain, its assumptions and how it said it would be measured.
2. Separate **volume** (records the automation handled, from its log or the movement log) from **result** (meetings, wins, days saved).
3. Compare the same month year on year, with the list of people active in each period; headcount changes explain a lot.
4. Put the measured number next to the projection and its assumptions; say which assumption was wrong if they differ.
5. Report in four blocks: context, inventory of automations, effect on volume and result, reading and limits.

## Example

"Did lead routing work?" Volume: leads assigned from the routing log; result: time from flag to owner before and after, with the same sellers; projection: about 160 lead-hours a month; reading: what the data supports and what it does not.

## Troubleshooting

- **No history before the automation**: say the comparison is not possible yet; never compare with a guess.
