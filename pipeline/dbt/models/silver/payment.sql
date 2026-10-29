with latest as ({{ latest_version('bronze', 'billing_payments', 'payment_id') }})

select
    cast(payment_id as integer) as payment_id,
    cast(invoice_id as integer) as invoice_id,
    cast(paid_at as date) as paid_at,
    cast(amount_usd as integer) as amount_usd,
    _batch_id as last_seen_batch_id
from latest
