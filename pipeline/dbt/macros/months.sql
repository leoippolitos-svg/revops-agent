{#
  The "as of" day of the data: the date of the newest daily export in bronze.
  Silver keeps the latest version of every company, and a company shows up in
  every export after it is created, so the newest batch id is the newest day.
#}
{% macro data_as_of() %}
    (select max(cast(replace(last_seen_batch_id, 'as_of=', '') as date)) from {{ ref('company') }})
{% endmacro %}


{#
  One row per calendar month from the month of `start_date_sql` to the month of
  the data's "as of" day. month_end is the last day of the month, or the "as of"
  day for the month still in progress, so we never look past the data.
#}
{% macro month_spine(start_date_sql) %}
    select
        cast(month_start as date) as month,
        least(last_day(cast(month_start as date)), {{ data_as_of() }}) as month_end
    from unnest(generate_series(
        date_trunc('month', ({{ start_date_sql }})),
        date_trunc('month', {{ data_as_of() }}),
        interval 1 month
    )) as spine(month_start)
{% endmacro %}
