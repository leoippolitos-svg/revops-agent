-- Per month of the MQL: how many of Marketing's MQLs led to a deal for the same company
-- within 30 days. One MQL counts once, however many deals followed.
with mqls as (
    select f.submission_id, f.submitted_at, ct.company_id
    from {{ ref('form_submission') }} as f
    join {{ ref('contact') }} as ct on ct.contact_id = f.contact_id
    where f.marketing_mql_flag
),

matched as (
    select
        m.submission_id,
        date_trunc('month', m.submitted_at)::date as month,
        max(case when d.deal_id is not null then 1 else 0 end) as has_deal
    from mqls as m
    left join {{ ref('deal') }} as d
        on d.company_id = m.company_id
        and d.created_at >= m.submitted_at
        and d.created_at <= m.submitted_at + interval 30 day
    group by 1, 2
)

select month, count(*) as marketing_mqls, sum(has_deal) as mqls_with_deal_30d
from matched
group by month
