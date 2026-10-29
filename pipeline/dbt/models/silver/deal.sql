with latest as ({{ latest_version('bronze', 'crm_deals', 'deal_id') }})

select
    cast(deal_id as integer) as deal_id,
    -- An empty text means the CRM has no company on this deal.
    cast(nullif(company_id, '') as integer) as company_id,
    nullif(company_id, '') is not null as has_company,
    cast(owner_id as integer) as owner_id,
    name,
    cast(amount_usd as integer) as amount_usd,
    stage,
    cast(created_at as date) as created_at,
    cast(nullif(closed_at, '') as date) as closed_at,
    _batch_id as last_seen_batch_id
from latest
