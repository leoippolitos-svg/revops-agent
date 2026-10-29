with latest as ({{ latest_version('bronze', 'crm_deal_stage_history', 'history_id') }})

select
    cast(history_id as integer) as history_id,
    cast(deal_id as integer) as deal_id,
    stage,
    cast(entered_at as date) as entered_at,
    _batch_id as last_seen_batch_id
from latest
