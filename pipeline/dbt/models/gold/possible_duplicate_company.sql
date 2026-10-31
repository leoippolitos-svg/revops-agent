-- Company records flagged as possible duplicates, one row each, grouped by the name
-- they share (ignoring case and spaces at the ends). A list for a person to review:
-- nothing here is merged, and flagged records are never deleted (cross-cutting-rules).
select
    company_id,
    name,
    lower(trim(name)) as name_key,
    count(*) over (partition by lower(trim(name))) as records_with_name,
    owner_id,
    created_at
from {{ ref('company') }}
where is_possible_duplicate
