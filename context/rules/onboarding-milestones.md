---
id: onboarding-milestones
title: Onboarding milestones
kind: rule
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [area-onboarding, closed-won-provisioning]
---

# Onboarding milestones

## Purpose

When an onboarding milestone advances and what evidence moves it, so the onboarding auto-advance and the agent apply the same rule. Onboarding managers and the automation read it. It does not define time to go-live (that is the onboarding metrics). Customer Success owns it; a change of evidence or order needs a pull request approved by Customer Success and RevOps.

## Rules

- The milestones are, in order: kickoff, configured, go_live, as in [[gold.onboarding_progress.current_milestone]].
- The product event `workspace_configured` moves a subscription from kickoff to configured.
- The product event `first_job_completed` moves a subscription from configured to go_live.
- A milestone is never skipped and never moved back. An event that does not fit the current milestone is listed for the onboarding manager, not applied.
- Every move is written to the movement log with who moved it, from where, to where and why.

## Owner and approvers

Customer Success owns the milestones; RevOps approves changes to the automation that applies them.
