with latest as ({{ latest_version('bronze', 'marketing_form_submissions', 'submission_id') }})

select
    cast(submission_id as integer) as submission_id,
    cast(contact_id as integer) as contact_id,
    cast(campaign_id as integer) as campaign_id,
    cast(submitted_at as date) as submitted_at,
    cast(cast(marketing_mql_flag as integer) as boolean) as marketing_mql_flag,
    _batch_id as last_seen_batch_id
from latest
