-- One row per subscription with the date of each onboarding milestone and the latest one
-- reached, so an automation can advance a milestone without reading silver.
select
    s.subscription_id,
    s.company_id,
    max(case when m.milestone = 'kickoff' then m.reached_at end) as kickoff_at,
    max(case when m.milestone = 'configured' then m.reached_at end) as configured_at,
    max(case when m.milestone = 'go_live' then m.reached_at end) as go_live_at,
    case
        when max(case when m.milestone = 'go_live' then 1 end) = 1 then 'go_live'
        when max(case when m.milestone = 'configured' then 1 end) = 1 then 'configured'
        when max(case when m.milestone = 'kickoff' then 1 end) = 1 then 'kickoff'
        else 'not_started'
    end as current_milestone
from {{ ref('subscription') }} as s
left join {{ ref('onboarding_milestone') }} as m
    on m.subscription_id = s.subscription_id
group by s.subscription_id, s.company_id
