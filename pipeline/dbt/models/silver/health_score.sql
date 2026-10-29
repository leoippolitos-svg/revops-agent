with latest as ({{ latest_version('bronze', 'cs_health_scores', 'score_id') }})

select
    cast(score_id as integer) as score_id,
    cast(company_id as integer) as company_id,
    cast(scored_at as date) as scored_at,
    cast(score as integer) as score,
    band,
    _batch_id as last_seen_batch_id
from latest
