-- One row per subscription with its status, its dates, and how many other active
-- subscriptions its company still has: a company is only deactivated when it has none.
select
    s.subscription_id,
    s.company_id,
    s.status,
    s.started_at,
    s.ended_at,
    (
        select count(*)
        from {{ ref('subscription') }} as other
        where other.company_id = s.company_id
            and other.subscription_id <> s.subscription_id
            and other.status = 'active'
    ) as other_active_subscriptions
from {{ ref('subscription') }} as s
