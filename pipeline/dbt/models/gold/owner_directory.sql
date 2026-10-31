-- One row per owner with the name and team, so the agent can say a person's name
-- instead of an id without reading silver. No e-mail or other contact detail.
select
    owner_id,
    full_name,
    team
from {{ ref('owner') }}
