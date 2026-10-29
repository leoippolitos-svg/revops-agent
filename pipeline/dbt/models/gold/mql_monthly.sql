-- Marketing and Sales count qualified leads differently; both counts, side by side.
select
    cast(date_trunc('month', f.submitted_at) as date) as month,
    count(*) as form_submissions,
    count(*) filter (where f.marketing_mql_flag) as marketing_mqls,
    count(*) filter (where c.sales_mql_flag) as sales_mqls,
    count(*) filter (where f.marketing_mql_flag <> c.sales_mql_flag) as conflicting_flags
from {{ ref('form_submission') }} as f
join {{ ref('contact') }} as c on c.contact_id = f.contact_id
group by 1
