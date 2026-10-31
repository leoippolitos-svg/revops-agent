-- Per month and campaign channel: the budget of campaigns that started in the month, the
-- form submissions and Marketing's MQLs they brought. Cost per MQL is budget over MQLs,
-- computed in the answer so the components stay visible.
with budget as (
    select date_trunc('month', started_at)::date as month, channel, sum(budget_usd) as budget_usd
    from {{ ref('campaign') }}
    group by 1, 2
),

submissions as (
    select
        date_trunc('month', f.submitted_at)::date as month,
        c.channel,
        count(*) as form_submissions,
        count(*) filter (where f.marketing_mql_flag) as marketing_mqls
    from {{ ref('form_submission') }} as f
    join {{ ref('campaign') }} as c on c.campaign_id = f.campaign_id
    group by 1, 2
)

select
    coalesce(s.month, b.month) || '|' || coalesce(s.channel, b.channel) as month_channel_key,
    coalesce(s.month, b.month) as month,
    coalesce(s.channel, b.channel) as channel,
    coalesce(b.budget_usd, 0) as budget_usd,
    coalesce(s.form_submissions, 0) as form_submissions,
    coalesce(s.marketing_mqls, 0) as marketing_mqls
from submissions as s
full outer join budget as b
    on b.month = s.month and b.channel = s.channel
