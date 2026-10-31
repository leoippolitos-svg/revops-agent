-- One row per deal with its stage and yearly amount, so the amount recalculation can
-- compare a new net amount with the current one without reading silver.
select
    deal_id,
    owner_id,
    stage,
    amount_usd
from {{ ref('deal') }}
