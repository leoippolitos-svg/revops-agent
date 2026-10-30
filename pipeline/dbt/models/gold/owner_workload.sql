-- Open deals per owner, so a routing rule can see who has room. Every owner is listed,
-- also those with no open deal, because an empty owner is the one with the most room.
select
    o.owner_id,
    o.team,
    count(d.deal_id) as open_deals,
    coalesce(sum(d.amount_usd), 0) as open_amount_usd
from {{ ref('owner') }} as o
left join {{ ref('deal') }} as d
    on d.owner_id = o.owner_id
    and d.stage not in ('closed_won', 'closed_lost')
group by 1, 2
