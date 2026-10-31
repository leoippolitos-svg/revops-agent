---
id: cross-cutting-rules
title: Cross-cutting rules
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-30
related: [active-customer, mrr, funnel-stages, mql]
---

# Cross-cutting rules

## Definition

These are the rules that apply to every analysis, whatever the metric: currency, dates, internal accounts, data-quality flags and which system is the source of truth. A metric document links here instead of repeating them. If a metric document contradicts this one, this one wins.

## Rules

- Currency: every amount is in US dollars. Examples are [[silver.deal.amount_usd]], [[silver.subscription.mrr_usd]] and [[silver.invoice.amount_usd]]. Amounts are whole dollars, never rounded further in a report.
- Dates: all dates are calendar dates, with no time of day and no time zone conversion. A month is a calendar month, and months in gold start on the first day, as in [[gold.mrr_monthly.month]].
- "As of": figures are as of the newest daily export loaded. The month in progress stops on that day and must not be compared with a full month.
- Internal and test accounts: companies and contacts that belong to Fernway itself, or that exist for testing, are excluded from every business metric. Fernway's data has none today. When one appears it must be flagged in silver first, so every metric excludes it the same way.
- Source of truth: the CRM for deals and the funnel ([[silver.deal.stage]]), billing for subscriptions, revenue and customers ([[silver.subscription.status]]), Customer Success for health scores ([[silver.health_score.band]]), and marketing forms for lead flags ([[silver.form_submission.marketing_mql_flag]]). When two systems disagree, the source of truth for that topic wins.
- Duplicate companies: a company record with the same name as another, ignoring letter case, is flagged by [[silver.company.is_possible_duplicate]]. Flagged records are never deleted. When counting companies, count flagged records separately and say so.
- Deals without a company: flagged by [[silver.deal.has_company]]. They stay in the funnel and are listed for the owner to fix. They cannot be attributed to a segment or a country.
- Subscriptions without a deal: flagged by [[silver.subscription.has_matching_deal]]. They still count for revenue and customers, because billing is the source of truth.
- How many records carry each flag above, as of the newest export, is in [[gold.data_quality_snapshot]]. Read the counts from there: the flagged records themselves stay in silver. Closed won deals with no subscription ([[gold.data_quality_snapshot.closed_won_without_subscription]]) include deals won in the last two weeks, because a subscription starts within two weeks of the win, so a small number is normal.
- Every answer states the definition it used, links the context document, names the source in plain words (the system and object, such as billing subscriptions) and lists the caveats that apply. Table and column names appear only when someone asks for them.

## Gotchas

- Two systems often use the same word for different things. "Customer" is a CRM stage for Sales and a paid subscription for Customer Success, see [[concept:active-customer]].
- A flag is not a filter. A flagged record is still in the numbers unless the metric document says it is excluded.
- Data-quality flags describe the data as exported. They can change when a source is corrected, so a number can move without any business change.
- Deals and subscriptions keep their current state only. A past date uses the dates recorded in history, for example [[silver.deal_stage_history.entered_at]].

## Team differences

None. Teams differ on the meaning of individual terms, and those differences are recorded in each metric's document. These rules hold for every team.

## Examples

A report on revenue by country joins [[gold.mrr_monthly.ending_mrr_usd]] to companies. Subscriptions whose company is a flagged duplicate stay in the total. The report states that some companies appear twice, and leaves them in. If the same report excluded test accounts, it would say so, because the rule excludes them from every metric.
