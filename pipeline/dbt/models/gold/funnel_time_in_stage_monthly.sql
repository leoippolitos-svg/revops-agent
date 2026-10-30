-- How long deals stayed in each open stage, by the month they left it.
-- A deal leaves a stage when it enters the next stage in funnel order, which may be
-- closed_won or closed_lost. Deals still in a stage have no exit yet and are not counted.
with ordered as (
    select
        deal_id,
        stage,
        entered_at,
        case stage
            when 'qualification' then 1
            when 'discovery' then 2
            when 'proposal' then 3
            when 'negotiation' then 4
            when 'closed_won' then 5
            when 'closed_lost' then 6
        end as stage_order
    from {{ ref('deal_stage_history') }}
),

exits as (
    select
        stage,
        stage_order,
        entered_at,
        lead(entered_at) over (partition by deal_id order by stage_order) as left_at
    from ordered
)

select
    cast(date_trunc('month', left_at) as date) as month,
    stage,
    stage_order,
    count(*) as deals_left,
    -- The CRM stores some dates out of order. Those exits would give a negative
    -- duration, so they are counted apart and kept out of the averages.
    count(*) filter (where left_at < entered_at) as out_of_order_exits,
    median(date_diff('day', entered_at, left_at)) filter (where left_at >= entered_at) as median_days_in_stage,
    avg(date_diff('day', entered_at, left_at)) filter (where left_at >= entered_at) as avg_days_in_stage,
    cast(date_trunc('month', left_at) as varchar) || '|' || stage as month_stage_key
from exits
where left_at is not null and stage_order <= 4
group by 1, 2, 3, 8
