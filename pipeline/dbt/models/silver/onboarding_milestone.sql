with latest as ({{ latest_version('bronze', 'cs_onboarding_milestones', 'milestone_id') }})

select
    cast(milestone_id as integer) as milestone_id,
    cast(subscription_id as integer) as subscription_id,
    milestone,
    cast(reached_at as date) as reached_at,
    _batch_id as last_seen_batch_id
from latest
