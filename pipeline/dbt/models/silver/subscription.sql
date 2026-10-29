with latest as ({{ latest_version('bronze', 'billing_subscriptions', 'subscription_id') }})

select
    cast(subscription_id as integer) as subscription_id,
    cast(deal_id as integer) as deal_id,
    -- True when the CRM still has the deal this subscription claims to come from.
    cast(deal_id as integer) in (select deal_id from {{ ref('deal') }}) as has_matching_deal,
    cast(company_id as integer) as company_id,
    plan,
    cast(mrr_usd as integer) as mrr_usd,
    status,
    cast(started_at as date) as started_at,
    cast(nullif(ended_at, '') as date) as ended_at,
    _batch_id as last_seen_batch_id
from latest
