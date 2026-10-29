with latest as ({{ latest_version('bronze', 'marketing_campaigns', 'campaign_id') }})

select
    cast(campaign_id as integer) as campaign_id,
    name,
    channel,
    cast(started_at as date) as started_at,
    cast(budget_usd as integer) as budget_usd,
    _batch_id as last_seen_batch_id
from latest
