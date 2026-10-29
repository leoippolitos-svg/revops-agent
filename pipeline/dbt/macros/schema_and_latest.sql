{#
  By default dbt names a custom schema "<default schema>_<custom schema>", which
  would give us main_silver. We want exactly "silver" and "gold" (data-modeling
  standard: the layer is the schema), so we use the custom name as it is.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}


{#
  Bronze keeps a row for every daily export, so one entity appears many times.
  This keeps only the row from the most recent batch for each key. The batch id
  looks like as_of=2026-01-02, so sorting it as text sorts it by date.
#}
{% macro latest_version(source_name, table_name, key) %}
    select * exclude (_version_rank)
    from (
        select
            *,
            row_number() over (partition by {{ key }} order by _batch_id desc) as _version_rank
        from {{ source(source_name, table_name) }}
    )
    where _version_rank = 1
{% endmacro %}
