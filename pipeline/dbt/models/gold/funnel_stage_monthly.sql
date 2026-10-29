-- How many deals entered each stage in each month.
select
    cast(date_trunc('month', h.entered_at) as date) as month,
    h.stage,
    case h.stage
        when 'qualification' then 1
        when 'discovery' then 2
        when 'proposal' then 3
        when 'negotiation' then 4
        when 'closed_won' then 5
        when 'closed_lost' then 6
    end as stage_order,
    count(distinct h.deal_id) as deals_entered,
    sum(d.amount_usd) as amount_usd_entered,
    cast(cast(date_trunc('month', h.entered_at) as date) as varchar) || '|' || h.stage as month_stage_key
from {{ ref('deal_stage_history') }} as h
join {{ ref('deal') }} as d on d.deal_id = h.deal_id
group by 1, 2, 3, 6
