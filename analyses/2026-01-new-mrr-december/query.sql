-- Question: new MRR fell in December. Is that the start of a slowdown?
-- Reads gold only. Run with run.py in this folder (read-only connection).

-- name: data_date
SELECT as_of AS data_as_of FROM gold.data_quality_snapshot;

-- name: new_mrr_by_month
-- January 2026 is still in progress, so it is left out (cross-cutting-rules: "As of").
SELECT
    month,
    new_mrr_usd,
    churned_mrr_usd,
    ending_mrr_usd,
    round(100.0 * (new_mrr_usd - lag(new_mrr_usd) OVER (ORDER BY month))
          / lag(new_mrr_usd) OVER (ORDER BY month), 1) AS new_mrr_change_pct
FROM gold.mrr_monthly
WHERE month < DATE '2026-01-01'
ORDER BY month;

-- name: closed_won_by_month
-- A won deal's yearly value divided by 12 is what its subscription adds to MRR (context: mrr).
-- The subscription starts up to two weeks after the win, so the two columns can differ a little.
SELECT
    f.month,
    f.deals_entered AS deals_won,
    f.amount_usd_entered AS yearly_value_won_usd,
    round(f.amount_usd_entered / f.deals_entered) AS avg_yearly_value_usd,
    round(f.amount_usd_entered / 12.0) AS implied_monthly_usd,
    m.new_mrr_usd
FROM gold.funnel_stage_monthly f
JOIN gold.mrr_monthly m USING (month)
WHERE f.stage = 'closed_won' AND f.month < DATE '2026-01-01'
ORDER BY f.month;

-- name: late_funnel_entries
-- Deals entering negotiation lead closed won by weeks, so they say what the next months look like.
SELECT
    month,
    max(deals_entered) FILTER (WHERE stage = 'proposal')    AS entered_proposal,
    max(deals_entered) FILTER (WHERE stage = 'negotiation') AS entered_negotiation,
    max(deals_entered) FILTER (WHERE stage = 'closed_won')  AS closed_won
FROM gold.funnel_stage_monthly
WHERE month < DATE '2026-01-01'
GROUP BY month
ORDER BY month;

-- name: mature_cohorts
-- Only cohorts at least 90 days past the end of their month are compared (context: funnel-stages).
-- November and December cohorts are not mature yet, so they do not appear.
SELECT
    c.cohort_month,
    c.deals_qualified,
    c.reached_proposal,
    c.closed_won,
    c.closed_lost,
    round(100.0 * c.closed_won / nullif(c.closed_won + c.closed_lost, 0), 1) AS win_rate_pct
FROM gold.funnel_conversion_monthly c
CROSS JOIN gold.data_quality_snapshot d
WHERE c.cohort_month + INTERVAL 1 MONTH + INTERVAL 90 DAY <= d.as_of
ORDER BY c.cohort_month;

-- name: data_flags
-- Rule out data causes first (cross-cutting-rules).
SELECT
    deals_without_company,
    deals,
    closed_won_without_subscription,
    closed_won_deals,
    subscriptions_without_deal,
    subscriptions
FROM gold.data_quality_snapshot;
