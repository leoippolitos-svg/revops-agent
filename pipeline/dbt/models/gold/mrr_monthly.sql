-- Monthly recurring revenue and its movements, one row per month.
with spine as (
    {{ month_spine("select min(started_at) from " ~ ref('subscription')) }}
),

movements as (
    select
        spine.month,
        coalesce(sum(s.mrr_usd) filter (
            where s.started_at <= spine.month_end
              and (s.ended_at is null or s.ended_at > spine.month_end)
        ), 0) as ending_mrr_usd,
        coalesce(sum(s.mrr_usd) filter (
            where date_trunc('month', s.started_at) = spine.month
        ), 0) as new_mrr_usd,
        coalesce(sum(s.mrr_usd) filter (
            where s.ended_at is not null
              and date_trunc('month', s.ended_at) = spine.month
        ), 0) as churned_mrr_usd
    from spine
    cross join {{ ref('subscription') }} as s
    group by spine.month
)

select
    month,
    -- What was left at the end of the previous month.
    coalesce(lag(ending_mrr_usd) over (order by month), 0) as starting_mrr_usd,
    new_mrr_usd,
    churned_mrr_usd,
    ending_mrr_usd
from movements
