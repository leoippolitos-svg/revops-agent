---
date: 2026-10-31
type: automation
pr: "#64"
author: Leonardo Ippolito
---

# Onboarding auto-advance, deactivation after churn, deal amount recalculation

## What was done
- `automations/onboarding-advance/`: moves a subscription to the next onboarding milestone when a product event is the evidence (`workspace_configured`, `first_job_completed`), never skips or moves back, sends anything out of order to a review list.
- `automations/churn-deactivation/`: daily, switches off a churned workspace after a 7-day grace period and marks the company inactive, unless the company has another active subscription; never deletes. Scheduled in the new `daily-automations.yml`.
- `automations/deal-amount/`: when a discount changes, calculates the net amount and writes a proposal that Finance approves item by item, with the sales lead above 20 percent; never writes the amount.
- `automations/_lib/movement_log.py`: one shared log of every change (who, what, from, to, why), keyed by id.
- Three gold models (`onboarding_progress`, `subscription_lifecycle`, `deal_amount`), three rule documents read at run time, two new write-back authorizations and the amount listed as proposal only, example event files, catalog cards, index rows and 9 tests.
- Every spec explains the problem, why the process exists, the projected gain with its assumptions, a diagram, where AI enters (nowhere), cost and monitoring.

## Why
These are the reference design's n8n flows (stage auto-advance with a movement log, deactivation after churn, net price recalculation), rebuilt as code in the repository under ADR-0024, on Fernway's data.

## Result or decision
- On the fictional data: two churned workspaces are past the grace period; of four example onboarding events, two advance and two go to review; of four discount changes, two become proposals.
- The amount follows the write-back rule for sensitive fields: proposals only, which differs on purpose from the original flow that wrote it.
- All effects are simulated; writes need their kill switch.

## Rules and context changed
New rule documents `onboarding-milestones`, `churn-deactivation`, `deal-discount`; `writeback-rules` gains `onboarding-advance`, `churn-deactivation` and the amount as proposal only.

## Follow-ups
The two automations with AI: site qualification and prospecting drafts.
