---
id: closed-won-provisioning
title: Closed won provisioning
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-30
related: [funnel-stages, active-customer, mrr, cross-cutting-rules]
---

# Closed won provisioning

## Definition

Provisioning is the step where a customer who just signed gets a workspace in the product and an onboarding kickoff. It starts when a deal enters closed_won and happens once per deal. Provisioning is not billing: it does not set the plan, the price or the start of revenue.

## Rules

- The trigger is a deal entering closed_won, the date in [[silver.deal_stage_history.entered_at]]. See [[concept:funnel-stages]].
- One deal is provisioned once. The deal identifier is the key, so running again for the same deal changes nothing.
- A deal with no company ([[silver.deal.has_company]]) is not provisioned. There is nobody to create a workspace for. It is listed for the owner to fix, see [[concept:cross-cutting-rules]].
- A deal whose company is flagged as a possible duplicate ([[silver.company.is_possible_duplicate]]) is held for a person to confirm the company. Provisioning twice for the same real company is the failure this rule prevents.
- A deal that already has a subscription is not provisioned again. The subscription means billing has started, see [[silver.subscription.deal_id]].
- The plan and the monthly price come from billing when the subscription starts ([[silver.subscription.plan]]), never from the CRM or from the automation.
- Onboarding follows the milestones kickoff, configured and go_live ([[silver.onboarding_milestone.milestone]]). Provisioning only requests the kickoff. The onboarding team records the others.
- A subscription starts within two weeks of the win. A closed_won deal still without a subscription after two weeks is listed for Finance. The size of that backlog is [[gold.data_quality_snapshot.closed_won_without_subscription]].

## Gotchas

- Provisioning does not make the company an active customer. A customer exists when the subscription has started and been paid, see [[concept:active-customer]]. Provisioned and not yet subscribed is the normal state for up to two weeks.
- A provisioned workspace creates no revenue. Revenue starts with the subscription, see [[concept:mrr]].
- [[gold.data_quality_snapshot.closed_won_without_subscription]] includes deals won in the last two weeks. A small number is normal and does not mean provisioning failed.
- A deal moved out of closed_won by mistake and back in is the same deal. The key keeps it from being provisioned a second time.

## Team differences

- Sales considers the customer won the day of the signature and wants the workspace at once. Customer Success counts the customer from the first payment and does not want a workspace for a company that may be a duplicate. **The rules above are canonical**: the workspace is created on the win, except for the cases that need a person.

## Examples

A deal enters closed_won on March 3. Its company has no duplicate flag, so a kickoff is requested the same day. The subscription starts on March 10 on the growth plan, and the company becomes an active customer once the first payment arrives. Running the automation again for the same deal on March 4 does nothing.
