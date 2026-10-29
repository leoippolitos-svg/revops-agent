with latest as ({{ latest_version('bronze', 'crm_companies', 'company_id') }})

select
    cast(company_id as integer) as company_id,
    name,
    industry,
    segment,
    cast(employee_count as integer) as employee_count,
    country,
    cast(owner_id as integer) as owner_id,
    cast(created_at as date) as created_at,
    -- Flagged, not deleted: deciding which copy wins is a business rule.
    count(*) over (partition by lower(name)) > 1 as is_possible_duplicate,
    _batch_id as last_seen_batch_id
from latest
