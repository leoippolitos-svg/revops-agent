-- Conversion by cohort: deals grouped by the month they entered qualification, and how
-- many of them ever reached each later stage. "Ever reached" looks only at whether the
-- stage row exists, so the out-of-order stage dates in the CRM cannot change the counts.
with reached as (
    select
        deal_id,
        min(case when stage = 'qualification' then entered_at end) as qualified_at,
        max(case when stage = 'discovery' then 1 else 0 end) as reached_discovery,
        max(case when stage = 'proposal' then 1 else 0 end) as reached_proposal,
        max(case when stage = 'negotiation' then 1 else 0 end) as reached_negotiation,
        max(case when stage = 'closed_won' then 1 else 0 end) as won,
        max(case when stage = 'closed_lost' then 1 else 0 end) as lost
    from {{ ref('deal_stage_history') }}
    group by 1
)

select
    cast(date_trunc('month', qualified_at) as date) as cohort_month,
    count(*) as deals_qualified,
    sum(reached_discovery) as reached_discovery,
    sum(reached_proposal) as reached_proposal,
    sum(reached_negotiation) as reached_negotiation,
    sum(won) as closed_won,
    sum(lost) as closed_lost,
    count(*) - sum(won) - sum(lost) as still_open
from reached
where qualified_at is not null
group by 1
