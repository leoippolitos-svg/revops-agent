with latest as ({{ latest_version('bronze', 'billing_invoices', 'invoice_id') }})

select
    cast(invoice_id as integer) as invoice_id,
    cast(subscription_id as integer) as subscription_id,
    cast(issued_at as date) as issued_at,
    cast(due_at as date) as due_at,
    cast(amount_usd as integer) as amount_usd,
    status,
    _batch_id as last_seen_batch_id
from latest
