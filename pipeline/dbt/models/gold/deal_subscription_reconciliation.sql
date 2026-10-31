-- One row per closed won deal or subscription, matched on the deal id the subscription
-- carries: an explicit id, never a name. The classification is what an audit acts on.
-- Amounts are compared as monthly values: a deal's yearly amount divided by 12 against
-- the subscription's MRR; the tolerance lives in the reconciliation automation's rules.
with won as (
    select deal_id, company_id, owner_id, amount_usd, closed_at
    from {{ ref('deal') }}
    where stage = 'closed_won'
),

subs as (
    select subscription_id, deal_id, company_id, mrr_usd, started_at
    from {{ ref('subscription') }}
)

select
    coalesce(w.deal_id, s.deal_id) as deal_id,
    s.subscription_id,
    coalesce(w.company_id, s.company_id) as company_id,
    w.owner_id,
    w.closed_at,
    s.started_at,
    w.amount_usd as deal_amount_usd,
    s.mrr_usd as subscription_mrr_usd,
    case
        when w.deal_id is null then 'subscription_without_deal'
        when s.subscription_id is null then 'won_without_subscription'
        else 'matched'
    end as match_status,
    case
        when w.deal_id is not null and s.subscription_id is not null
            then round(w.amount_usd / 12.0 - s.mrr_usd, 2)
    end as monthly_gap_usd
from won as w
full outer join subs as s
    on s.deal_id = w.deal_id
