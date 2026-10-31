---
name: detect-risk
description: "Lists accounts at risk of churn from health band, open high-priority tickets and missed onboarding milestones, each with the signal that put it on the list. Use when someone asks which customers are at risk, which accounts need attention, or who might churn this quarter."
---

# Detect risk

## Steps

1. Read `area-customer-success` and `metrics-customer-success`. A risk is a signal, not a churn: never call an account churned until billing says so.
2. Check which signals exist in gold. Health band, tickets and onboarding milestones are not in gold yet: say it is a data task and stop, instead of reading silver.
3. When the gold models exist: list accounts whose latest band is red, or with an open high-priority ticket older than 14 days, or with a kickoff and no go-live after 60 days.
4. For each account give the signal, its date and the owner's name (map tool), never an id.
5. Order by MRR at risk, from the subscription value.
6. End with two or three cuts: by owner, by segment, by signal.

## Example

"Which customers are at risk?" Today: "Health band, tickets and onboarding are not in gold yet, so I cannot list at-risk accounts from governed data; this needs gold models for them (listed in the backlog)."

## Troubleshooting

- **The list is every red account**: a band alone is a weak signal; show the combination of signals for each.
