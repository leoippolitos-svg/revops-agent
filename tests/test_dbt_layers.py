"""Builds bronze from generated data, runs dbt on it and checks the silver and gold layers."""

import sys
from pathlib import Path

import duckdb
import pytest
from dbt.adapters.factory import cleanup_connections, reset_adapters
from dbt.cli.main import dbtRunner

ROOT = Path(__file__).resolve().parents[1]
# Both are scripts, not installed packages, so we add their folders to the import path.
sys.path.insert(0, str(ROOT / "generator"))
sys.path.insert(0, str(ROOT / "pipeline"))

import generate  # noqa: E402
import ingest  # noqa: E402

DBT_DIR = ROOT / "pipeline" / "dbt"


@pytest.fixture(scope="module")
def lakehouse(tmp_path_factory, monkeypatch_module):
    """Initial load plus 10 days into bronze, then `dbt build` on top. Built once."""
    work = tmp_path_factory.mktemp("lakehouse")
    db_path = work / "lakehouse.duckdb"
    raw = work / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=10)
    ingest.ingest(raw, db_path)

    monkeypatch_module.setenv("LAKEHOUSE_PATH", str(db_path))
    result = dbtRunner().invoke([
        "build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR),
        "--target-path", str(work / "target"), "--log-path", str(work / "logs"),
    ])
    # dbt runs inside this process and keeps its connection to the DuckDB file
    # open; DuckDB allows one configuration per file at a time, so we let go of
    # it before the tests open the file read-only.
    cleanup_connections()
    reset_adapters()
    return db_path, result


@pytest.fixture(scope="module")
def monkeypatch_module():
    # pytest's own monkeypatch lasts one test; this one lasts the whole module.
    with pytest.MonkeyPatch.context() as patch:
        yield patch


def query(db_path, sql):
    con = duckdb.connect(str(db_path))  # same configuration dbt used, see the fixture
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_dbt_build_passes_every_model_and_every_test(lakehouse):
    _, result = lakehouse
    assert result.success, result.exception
    statuses = {str(r.status) for r in result.result}
    assert statuses <= {"success", "pass"}


def test_silver_has_one_row_per_entity(lakehouse):
    db, _ = lakehouse
    for table, key in [("company", "company_id"), ("deal", "deal_id"), ("invoice", "invoice_id"),
                       ("contact", "contact_id"), ("subscription", "subscription_id")]:
        total, distinct = query(db, f"SELECT count(*), count(DISTINCT {key}) FROM silver.{table}")[0]
        assert total == distinct > 0, table


def test_silver_keeps_the_same_entities_bronze_has(lakehouse):
    db, _ = lakehouse
    in_bronze = query(db, "SELECT count(DISTINCT deal_id) FROM bronze.crm_deals")[0][0]
    assert query(db, "SELECT count(*) FROM silver.deal")[0][0] == in_bronze


def test_silver_keeps_the_latest_version(lakehouse):
    db, _ = lakehouse
    # For every deal, the silver stage equals the stage in its most recent batch.
    wrong = query(db, """
        SELECT count(*) FROM silver.deal d
        JOIN (SELECT deal_id, arg_max(stage, _batch_id) AS stage FROM bronze.crm_deals GROUP BY deal_id) b
          ON b.deal_id = cast(d.deal_id AS varchar)
        WHERE b.stage <> d.stage""")[0][0]
    assert wrong == 0


def test_silver_columns_are_typed(lakehouse):
    db, _ = lakehouse
    types = {r[0]: r[1] for r in query(db, """
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_schema = 'silver' AND table_name = 'deal'""")}
    assert types["deal_id"] == "INTEGER" and types["amount_usd"] == "INTEGER"
    assert types["created_at"] == "DATE" and types["closed_at"] == "DATE"
    assert types["has_company"] == "BOOLEAN"


def test_data_quality_issues_are_flagged_not_hidden(lakehouse):
    db, _ = lakehouse
    # The generator plants these; silver must still show them, with a flag.
    assert query(db, "SELECT count(*) FROM silver.company WHERE is_possible_duplicate")[0][0] > 0
    assert query(db, "SELECT count(*) FROM silver.deal WHERE NOT has_company")[0][0] > 0
    assert query(db, "SELECT count(*) FROM silver.subscription WHERE NOT has_matching_deal")[0][0] > 0


def test_there_is_a_silver_schema_not_a_prefix(lakehouse):
    db, _ = lakehouse
    schemas = {r[0] for r in query(db, "SELECT schema_name FROM information_schema.schemata")}
    assert "silver" in schemas and "main_silver" not in schemas


# --- Gold ---------------------------------------------------------------------

def test_there_is_a_gold_schema_not_a_prefix(lakehouse):
    db, _ = lakehouse
    schemas = {r[0] for r in query(db, "SELECT schema_name FROM information_schema.schemata")}
    assert "gold" in schemas and "main_gold" not in schemas


def test_mrr_months_connect_and_add_up(lakehouse):
    db, _ = lakehouse
    rows = query(db, "SELECT month, starting_mrr_usd, new_mrr_usd, churned_mrr_usd, ending_mrr_usd "
                     "FROM gold.mrr_monthly ORDER BY month")
    assert len(rows) > 1
    previous_ending = 0
    for month, starting, new, churned, ending in rows:
        assert starting == previous_ending, month
        assert starting + new - churned == ending, month
        previous_ending = ending


def test_ending_mrr_of_the_last_month_matches_the_subscriptions_in_force(lakehouse):
    db, _ = lakehouse
    last_month_ending = query(db, "SELECT ending_mrr_usd FROM gold.mrr_monthly ORDER BY month DESC LIMIT 1")[0][0]
    # Independent check straight from silver: subscriptions that have not ended.
    in_force = query(db, "SELECT sum(mrr_usd) FROM silver.subscription WHERE ended_at IS NULL")[0][0]
    assert last_month_ending == in_force


def test_new_mrr_over_all_months_is_the_mrr_of_every_subscription(lakehouse):
    db, _ = lakehouse
    total_new = query(db, "SELECT sum(new_mrr_usd) FROM gold.mrr_monthly")[0][0]
    assert total_new == query(db, "SELECT sum(mrr_usd) FROM silver.subscription")[0][0]


def test_active_customers_are_counted_per_company(lakehouse):
    db, _ = lakehouse
    for month, customers, subscriptions in query(
            db, "SELECT month, active_customers, active_subscriptions "
                "FROM gold.active_customer_monthly ORDER BY month"):
        assert 0 <= customers <= subscriptions, month
    # The last month, straight from silver: a company counts once, and only if paid.
    last = query(db, "SELECT active_customers FROM gold.active_customer_monthly ORDER BY month DESC LIMIT 1")[0][0]
    expected = query(db, """
        SELECT count(DISTINCT s.company_id) FROM silver.subscription s
        WHERE s.ended_at IS NULL
          AND EXISTS (SELECT 1 FROM silver.invoice i JOIN silver.payment p ON p.invoice_id = i.invoice_id
                      WHERE i.subscription_id = s.subscription_id)""")[0][0]
    assert last == expected


def test_a_month_never_has_active_customers_without_any_mrr(lakehouse):
    # MRR counts a subscription from its start day; an active customer also needs a
    # first payment, so a month can have MRR and no active customer yet, never the reverse.
    db, _ = lakehouse
    bad = query(db, """
        SELECT count(*) FROM gold.active_customer_monthly a JOIN gold.mrr_monthly m USING (month)
        WHERE a.active_customers > 0 AND m.ending_mrr_usd = 0""")[0][0]
    assert bad == 0


def test_funnel_entries_add_up_to_the_stage_history(lakehouse):
    db, _ = lakehouse
    in_gold = query(db, "SELECT sum(deals_entered) FROM gold.funnel_stage_monthly")[0][0]
    in_silver = query(db, "SELECT count(*) FROM silver.deal_stage_history")[0][0]
    assert in_gold == in_silver
    # Stages are numbered 1 to 6 in funnel order.
    order = dict(query(db, "SELECT DISTINCT stage, stage_order FROM gold.funnel_stage_monthly"))
    assert order["qualification"] == 1 and order["closed_won"] == 5 and order["closed_lost"] == 6


def test_mql_counts_add_up_and_disagreements_are_visible(lakehouse):
    db, _ = lakehouse
    submissions, marketing, sales, conflicts = query(db, """
        SELECT sum(form_submissions), sum(marketing_mqls), sum(sales_mqls), sum(conflicting_flags)
        FROM gold.mql_monthly""")[0]
    assert submissions == query(db, "SELECT count(*) FROM silver.form_submission")[0][0]
    assert marketing == query(db, "SELECT count(*) FROM silver.form_submission WHERE marketing_mql_flag")[0][0]
    assert 0 < conflicts < submissions and marketing != sales


def test_data_quality_snapshot_matches_the_silver_flags_and_the_answer_key(lakehouse):
    db, _ = lakehouse
    row = query(db, "SELECT * FROM gold.data_quality_snapshot")
    assert len(row) == 1
    (as_of, companies, dup, deals, no_company, subs, no_deal, won, won_no_sub) = row[0]
    # Same counts as the flags in silver.
    assert dup == query(db, "SELECT count(*) FROM silver.company WHERE is_possible_duplicate")[0][0] > 0
    assert no_company == query(db, "SELECT count(*) FROM silver.deal WHERE NOT has_company")[0][0] > 0
    assert no_deal == query(db, "SELECT count(*) FROM silver.subscription WHERE NOT has_matching_deal")[0][0] > 0
    assert companies == query(db, "SELECT count(*) FROM silver.company")[0][0]
    assert deals == query(db, "SELECT count(*) FROM silver.deal")[0][0]
    assert subs == query(db, "SELECT count(*) FROM silver.subscription")[0][0]
    # A flagged count never exceeds its total, and the as-of date is the newest export.
    assert dup <= companies and no_company <= deals and no_deal <= subs and won_no_sub <= won
    assert str(as_of) == query(db, "SELECT max(replace(last_seen_batch_id, 'as_of=', '')) FROM silver.company")[0][0]


def test_funnel_conversion_cohorts_add_up_and_never_grow_down_the_funnel(lakehouse):
    db, _ = lakehouse
    # Every deal with a qualification row is in exactly one cohort.
    qualified = query(db, "SELECT count(DISTINCT deal_id) FROM silver.deal_stage_history WHERE stage = 'qualification'")[0][0]
    assert query(db, "SELECT sum(deals_qualified) FROM gold.funnel_conversion_monthly")[0][0] == qualified
    # Won and lost match the stage history, and the open deals are what is left.
    won = query(db, "SELECT count(DISTINCT deal_id) FROM silver.deal_stage_history WHERE stage = 'closed_won'")[0][0]
    assert query(db, "SELECT sum(closed_won) FROM gold.funnel_conversion_monthly")[0][0] == won
    assert query(db, "SELECT count(*) FROM gold.funnel_conversion_monthly WHERE still_open < 0") == [(0,)]
    # Each later stage is reached by no more deals than the one before it.
    bad = query(db, """
        SELECT count(*) FROM gold.funnel_conversion_monthly
        WHERE reached_discovery > deals_qualified OR reached_proposal > reached_discovery
           OR reached_negotiation > reached_proposal""")[0][0]
    assert bad == 0


def test_time_in_stage_counts_every_exit_and_keeps_bad_dates_out_of_the_averages(lakehouse):
    db, _ = lakehouse
    # A deal exits every open stage it entered, except the stage it is in now.
    # Each deal has one row per stage, so exits = open-stage rows minus deals still in an open stage.
    exits = query(db, """
        SELECT count(*) FROM silver.deal_stage_history h JOIN silver.deal d USING (deal_id)
        WHERE h.stage IN ('qualification','discovery','proposal','negotiation') AND h.stage <> d.stage""")[0][0]
    assert query(db, "SELECT sum(deals_left) FROM gold.funnel_time_in_stage_monthly")[0][0] == exits
    # No negative day figure ever reaches the averages, and out-of-order exits never exceed exits.
    assert query(db, "SELECT count(*) FROM gold.funnel_time_in_stage_monthly WHERE median_days_in_stage < 0 OR avg_days_in_stage < 0") == [(0,)]
    assert query(db, "SELECT count(*) FROM gold.funnel_time_in_stage_monthly WHERE out_of_order_exits > deals_left") == [(0,)]


def test_owner_workload_lists_every_owner_and_counts_only_open_deals(lakehouse):
    db, _ = lakehouse
    assert query(db, "SELECT count(*) FROM gold.owner_workload")[0][0] == query(db, "SELECT count(*) FROM silver.owner")[0][0]
    open_deals = query(db, "SELECT count(*) FROM silver.deal WHERE stage NOT IN ('closed_won', 'closed_lost')")[0][0]
    assert query(db, "SELECT sum(open_deals) FROM gold.owner_workload")[0][0] == open_deals
    # An owner with no open deal still has a row, with zeros and not nulls.
    assert query(db, "SELECT count(*) FROM gold.owner_workload WHERE open_deals = 0 AND open_amount_usd <> 0") == [(0,)]
