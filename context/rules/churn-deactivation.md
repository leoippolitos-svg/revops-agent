---
id: churn-deactivation
title: Deactivation after churn
kind: rule
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [active-customer, closed-won-provisioning]
---

# Deactivation after churn

## Purpose

When a churned customer's workspace is switched off and the company marked inactive, so access never outlives the contract and the CRM shows who is still a customer. The deactivation automation and the agent read it. It does not define churn (that is billing's subscription status). Customer Success owns it with Finance.

## Rules

- A workspace is deactivated 7 days after its subscription ended, read from [[gold.subscription_lifecycle.ended_at]]: the grace period lets a renewal in progress land.
- It is deactivated only when the company has no other active subscription, from [[gold.subscription_lifecycle.other_active_subscriptions]].
- Deactivation switches off access; it never deletes the workspace or its data.
- The company is marked inactive in the CRM in the same run, and both changes go to the movement log.

## Owner and approvers

Customer Success owns the rule; Finance approves a change to the grace period.
