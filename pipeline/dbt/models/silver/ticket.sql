with latest as ({{ latest_version('bronze', 'cs_tickets', 'ticket_id') }})

select
    cast(ticket_id as integer) as ticket_id,
    cast(company_id as integer) as company_id,
    cast(opened_at as date) as opened_at,
    cast(nullif(closed_at, '') as date) as closed_at,
    priority,
    category,
    _batch_id as last_seen_batch_id
from latest
