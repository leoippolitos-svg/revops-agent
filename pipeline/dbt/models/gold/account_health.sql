-- The latest health score of each company, so "which accounts are at risk" has a gold
-- source. The score is a reading of the present, not a churn prediction (revops-methodologies).
with ranked as (
    select
        company_id,
        scored_at,
        score,
        band,
        row_number() over (partition by company_id order by scored_at desc, score_id desc) as recency
    from {{ ref('health_score') }}
)

select company_id, scored_at as latest_scored_at, score as latest_score, band as latest_band
from ranked
where recency = 1
