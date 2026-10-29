---
id: mql
title: Marketing qualified lead
owner_team: Marketing
status: canonical
last_reviewed: 2026-10-29
related: [funnel-stages, cross-cutting-rules]
---

# Marketing qualified lead

## Definition

A marketing qualified lead (MQL) is a contact who filled in a marketing form and whose submission Marketing flagged as ready for Sales. Marketing's flag is the one that counts. Sales keeps its own flag, which measures whether Sales agrees, and is never used to count MQLs.

## Rules

- The MQL count is Marketing's flag on the form submission: [[silver.form_submission.marketing_mql_flag]], summed by month as [[gold.mql_monthly.marketing_mqls]].
- A submission belongs to the month it was submitted: [[silver.form_submission.submitted_at]].
- Sales' flag lives on the contact: [[silver.contact.sales_mql_flag]], counted as [[gold.mql_monthly.sales_mqls]]. It is read as "Sales agrees this lead is ready", and the gap between the two flags is [[gold.mql_monthly.conflicting_flags]].
- Why Marketing's flag is canonical: it is set from the same form scoring for every lead, so it can be audited and repeated. Sales' flag is a personal judgment and varies by person.
- A contact who never filled in a form is not an MQL.
- MQL is the step before the sales funnel. A flagged lead becomes a deal in qualification, see [[concept:funnel-stages]].

## Gotchas

- When someone asks for "MQLs", answer with Marketing's count and say it is Marketing's flag. Mention Sales' count only when the question is about agreement or handoff quality.
- The two counts differ every month, so they must never be added or averaged.
- Form submissions ([[gold.mql_monthly.form_submissions]]) are not MQLs: most submissions are never flagged.
- The Sales flag does not change with time: it is the same before and after the form submission, so it cannot show how fast Sales reacted.
- Test submissions from internal addresses never count, see [[concept:cross-cutting-rules]].

## Team differences

- Marketing counts a lead as an MQL when its scoring flags the submission. **This is canonical.**
- Sales counts a lead as ready when the SDR agrees. That is a second opinion on the same lead, not a second definition of MQL.
- Disagreements are reviewed together every week. A rising [[gold.mql_monthly.conflicting_flags]] is the signal that lead scoring needs tuning.

## Examples

In a month with 30 form submissions, Marketing flags 12 and Sales flags 11, and they disagree on 1. The MQL count is 12. Sales' agreement count is 11, and the disagreement is 1 lead to review.
