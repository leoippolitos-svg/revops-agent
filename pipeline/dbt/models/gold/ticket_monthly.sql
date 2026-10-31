-- Support tickets opened and closed per month, category and priority. A month with no
-- ticket of a kind has no row: treat it as zero.
with opened as (
    select date_trunc('month', opened_at)::date as month, category, priority, count(*) as tickets_opened
    from {{ ref('ticket') }}
    group by 1, 2, 3
),

closed as (
    select date_trunc('month', closed_at)::date as month, category, priority, count(*) as tickets_closed
    from {{ ref('ticket') }}
    where closed_at is not null
    group by 1, 2, 3
)

select
    coalesce(o.month, c.month) || '|' || coalesce(o.category, c.category) || '|' || coalesce(o.priority, c.priority) as month_category_priority_key,
    coalesce(o.month, c.month) as month,
    coalesce(o.category, c.category) as category,
    coalesce(o.priority, c.priority) as priority,
    coalesce(o.tickets_opened, 0) as tickets_opened,
    coalesce(c.tickets_closed, 0) as tickets_closed
from opened as o
full outer join closed as c
    on c.month = o.month and c.category = o.category and c.priority = o.priority
