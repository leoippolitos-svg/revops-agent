-- One row: how many records carry each data-quality flag, as of the newest export.
-- The flags live in silver; this table exposes only their counts, so the agent and
-- the weekly audit can read them without touching silver.
select
    {{ data_as_of() }} as as_of,
    (select count(*) from {{ ref('company') }}) as companies,
    (select count(*) from {{ ref('company') }} where is_possible_duplicate) as possible_duplicate_companies,
    (select count(*) from {{ ref('deal') }}) as deals,
    (select count(*) from {{ ref('deal') }} where not has_company) as deals_without_company,
    (select count(*) from {{ ref('subscription') }}) as subscriptions,
    (select count(*) from {{ ref('subscription') }} where not has_matching_deal) as subscriptions_without_deal,
    (select count(*) from {{ ref('deal') }} where stage = 'closed_won') as closed_won_deals,
    (select count(*) from {{ ref('deal') }} as d
        where d.stage = 'closed_won'
          and d.deal_id not in (select deal_id from {{ ref('subscription') }})) as closed_won_without_subscription
