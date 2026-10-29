-- Customers with a current, paid subscription at the end of each month.
with spine as (
    {{ month_spine("select min(started_at) from " ~ ref('subscription')) }}
),

first_payment as (
    select
        i.subscription_id,
        min(p.paid_at) as first_paid_at
    from {{ ref('payment') }} as p
    join {{ ref('invoice') }} as i on i.invoice_id = p.invoice_id
    group by i.subscription_id
),

subscriptions as (
    select s.*, f.first_paid_at
    from {{ ref('subscription') }} as s
    left join first_payment as f on f.subscription_id = s.subscription_id
)

select
    spine.month,
    -- Counted per company: two subscriptions of one company are one customer.
    count(distinct s.company_id) filter (
        where s.started_at <= spine.month_end
          and (s.ended_at is null or s.ended_at > spine.month_end)
          and s.first_paid_at <= spine.month_end
    ) as active_customers,
    count(*) filter (
        where s.started_at <= spine.month_end
          and (s.ended_at is null or s.ended_at > spine.month_end)
          and s.first_paid_at <= spine.month_end
    ) as active_subscriptions
from spine
cross join subscriptions as s
group by spine.month
