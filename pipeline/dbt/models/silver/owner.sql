with latest as ({{ latest_version('bronze', 'crm_owners', 'owner_id') }})

select
    cast(owner_id as integer) as owner_id,
    full_name,
    email,
    team,
    _batch_id as last_seen_batch_id
from latest
