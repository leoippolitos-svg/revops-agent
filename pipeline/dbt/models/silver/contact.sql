with latest as ({{ latest_version('bronze', 'crm_contacts', 'contact_id') }})

select
    cast(contact_id as integer) as contact_id,
    cast(company_id as integer) as company_id,
    first_name,
    last_name,
    email,
    job_title,
    cast(created_at as date) as created_at,
    cast(cast(sales_mql_flag as integer) as boolean) as sales_mql_flag,
    _batch_id as last_seen_batch_id
from latest
