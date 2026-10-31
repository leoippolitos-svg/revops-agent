---
name: detect-risk
description: "Lists accounts at risk of churn from health band, open high-priority tickets and missed onboarding milestones, each with the signal that put it on the list. Use when someone asks which customers are at risk, which accounts need attention, or who might churn this quarter."
---

# Detect risk

## Steps

1. Read `area-customer-success` and `metrics-customer-success`. A risk is a signal, not a churn: never call an account churned until billing says so.
2. Read the signals from gold, each one on its own: a red latest band (`gold.account_health`), onboarding stuck in kickoff or configured for more than 60 days (`gold.onboarding_progress`), and the ticket trend by priority (`gold.ticket_monthly`).
3. List each account with every signal it shows, its date and the owner's name (map tool), never an id.
4. Order by MRR at risk, from the subscription value, and give the count of accounts per signal.
5. Say what is not covered: there is no product usage source, so adoption is not a signal yet.
6. End with two or three cuts: by owner, by segment, by signal.

## Example

"Which customers are at risk?" "Two accounts are in the red band and one subscription has been in kickoff for 70 days; tickets of high priority rose this month. Usage is not in the data, so adoption is not part of this list."

## Method

Sections 3.5 and 4 of `docs/standards/revops-methodologies.md`: early warning signals stay separate from the health score; a criterion with no source is not zero (re-normalise and label the score partial); a health score reads the present, it does not predict churn.

## Troubleshooting

- **The list is every red account**: a band alone is a weak signal; show the combination of signals for each.
