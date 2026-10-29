---
id: mql
title: Marketing qualified lead
owner_team: Marketing
status: draft
last_reviewed: 2026-10-29
related: [funnel-stages]
---

# Marketing qualified lead

## Definition

A marketing qualified lead (MQL) is a contact who filled in a marketing form and was judged ready to be handed to Sales. Marketing and Sales each keep their own flag for this, and the two do not always agree.

## Rules

- Marketing's flag is set on the form submission: [[silver.form_submission.marketing_mql_flag]].
- Sales' flag is set on the contact: [[silver.contact.sales_mql_flag]].
- A contact who never filled in a form is not an MQL for Sales in the data today.
- Report both counts, never only one: [[gold.mql_monthly.marketing_mqls]] and [[gold.mql_monthly.sales_mqls]], with the number of disagreements in [[gold.mql_monthly.conflicting_flags]].
- Month is the month of the form submission: [[silver.form_submission.submitted_at]].

## Gotchas

- The two counts differ every month. A number called "MQLs" with no owner named is ambiguous: say whose flag it is.
- The Sales flag does not change with time: it is the same before and after the form submission.
- Form submissions ([[gold.mql_monthly.form_submissions]]) are not MQLs: most submissions are never flagged by either team.

## Team differences

- Marketing counts a submission as an MQL when its own flag is set.
- Sales counts a contact as an MQL when its own flag is set.
- **Open decision for the owner: which one is canonical.** Until it is decided, answers must state which flag they used and show the other.

## Examples

In a month with 30 form submissions, Marketing flags 12 and Sales flags 11, and they disagree on 1. Marketing's MQL count is 12, Sales' is 11, and an answer about "MQLs this month" must say both.
