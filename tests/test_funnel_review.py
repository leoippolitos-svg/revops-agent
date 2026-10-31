"""Tests for automations/funnel-review/review.py, against hand-built gold tables."""

import importlib.util
import shutil
from datetime import date
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("funnel_review", ROOT / "automations" / "funnel-review" / "review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

AS_OF = date(2026, 1, 9)
TODAY = date(2026, 1, 12)
# Mature cohorts as of 2026-01-09: 2025-03 to 2025-09. The recent period is 07, 08, 09; the previous is 04, 05, 06.
MONTHS = [date(2025, m, 1) for m in range(3, 11)]
STAGE_CODE = "CREATE TABLE gold.funnel_stage_monthly (month_stage_key VARCHAR, month DATE, stage VARCHAR, stage_order INT, deals_entered INT, amount_usd_entered INT)"


def cohort(month, qualified=40, discovery=30, proposal=20, negotiation=12, won=6, lost=4, still_open=2):
    return (month, qualified, discovery, proposal, negotiation, won, lost, still_open)


def make_db(path: Path, recent=None, previous=None, as_of=AS_OF, time_days=None) -> Path:
    """Flat cohorts by default, so nothing moves. `recent` and `previous` override the three cohorts of each period."""
    recent_over, previous_over = recent or {}, previous or {}
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute(STAGE_CODE)
    con.execute("CREATE TABLE gold.funnel_conversion_monthly (cohort_month DATE, deals_qualified INT, reached_discovery INT, "
                "reached_proposal INT, reached_negotiation INT, closed_won INT, closed_lost INT, still_open INT)")
    for m in MONTHS:
        over = recent_over if m.month in (7, 8, 9) else previous_over if m.month in (4, 5, 6) else {}
        con.execute("INSERT INTO gold.funnel_conversion_monthly VALUES (?,?,?,?,?,?,?,?)", list(cohort(m, **over)))
    con.execute("CREATE TABLE gold.funnel_time_in_stage_monthly (month_stage_key VARCHAR, month DATE, stage VARCHAR, stage_order INT, "
                "deals_left INT, out_of_order_exits INT, median_days_in_stage DOUBLE, avg_days_in_stage DOUBLE)")
    for m in MONTHS:
        for i, stage in enumerate(review.OPEN_STAGES, 1):
            days = (time_days or {}).get((stage, m.month in (7, 8, 9)), 10.0)
            con.execute("INSERT INTO gold.funnel_time_in_stage_monthly VALUES (?,?,?,?,?,0,?,?)", [f"{m}|{stage}", m, stage, i, 10, days, days])
    con.execute("CREATE TABLE gold.data_quality_snapshot (as_of DATE)")
    con.execute("INSERT INTO gold.data_quality_snapshot VALUES (?)", [as_of])
    con.close()
    return path


@pytest.fixture
def db(tmp_path):
    return make_db(tmp_path / "lake.duckdb")


def report(db, flags=(), today=TODAY, rules=None):
    return review.build_report(review.read_gold(db), rules or review.load_rules(), today, list(flags))


# --- the rules come from the context document ---------------------------------------------

def test_the_thresholds_are_read_from_the_document():
    assert review.load_rules() == {"maturity_days": 90, "min_deals": 20}


def test_changing_the_document_changes_the_maturity_with_no_code_change(tmp_path):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    doc = context / "concepts" / "funnel-stages.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("mature once 90 days", "mature once 120 days"), encoding="utf-8")
    assert review.load_rules(context)["maturity_days"] == 120


def test_a_document_that_no_longer_says_them_stops_the_run(tmp_path):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    (context / "concepts" / "funnel-stages.md").write_text("# x\n", encoding="utf-8")
    with pytest.raises(review.ReviewError):
        review.load_rules(context)


# --- cohorts ---------------------------------------------------------------------------------

def test_only_mature_cohorts_are_compared(db):
    con = duckdb.connect(str(db), read_only=True)
    rows = review._rows(con, "funnel_conversion_monthly")
    con.close()
    got = [r["cohort_month"] for r in review.mature_cohorts(rows, AS_OF, 90)]
    assert got == MONTHS[:-1] and date(2025, 10, 1) not in got  # October ends 2025-10-31, mature on 2026-01-29


def test_the_report_names_the_two_periods(db):
    assert "recent 2025-07 to 2025-09" in report(db) and "previous 2025-04 to 2025-06" in report(db)


# --- the finding -----------------------------------------------------------------------------

def test_a_flat_funnel_says_nothing_changed_and_invents_no_bottleneck(db):
    out = report(db)
    assert "No stage changed beyond its normal range." in out and "Constraint" not in out


def test_the_stage_whose_conversion_fell_most_is_the_constraint(tmp_path):
    db = make_db(tmp_path / "l.duckdb", recent={"proposal": 12, "negotiation": 7, "won": 3})
    out = report(db)
    assert "**Constraint: proposal.**" in out and "Owner team to ask: sales." in out


def test_the_drop_is_weighted_by_volume_not_just_by_size(tmp_path):
    # Qualification to discovery drops 10 points on 40 deals; negotiation to won drops 20 points on 12 deals.
    db = make_db(tmp_path / "l.duckdb", recent={"discovery": 26, "proposal": 26, "negotiation": 12, "won": 3})
    assert "**Constraint: discovery.**" in report(db)


def test_a_small_change_does_not_name_a_constraint(tmp_path):
    db = make_db(tmp_path / "l.duckdb", recent={"discovery": 29})  # a drop of 2.5 points
    assert "Constraint" not in report(db)


def test_time_in_stage_names_a_constraint_when_no_conversion_moved(tmp_path):
    db = make_db(tmp_path / "l.duckdb", time_days={("negotiation", True): 30.0})
    out = report(db)
    assert "**Constraint: negotiation.**" in out and "time in negotiation grew" in out


def test_the_report_always_says_the_open_deals_next_to_the_time_in_stage(db):
    assert "Still open in these cohorts: recent 6, previous 6." in report(db)


def test_the_report_never_states_a_cause_and_says_the_loss_reason_is_unavailable(tmp_path):
    out = report(make_db(tmp_path / "l.duckdb", recent={"proposal": 12, "negotiation": 7, "won": 3}))
    assert "Likely cause: not stated here" in out and "Loss reason: unavailable" in out
    assert "because" not in out.lower()


def test_an_audit_flag_is_stated_before_the_finding(tmp_path):
    out = report(make_db(tmp_path / "l.duckdb", recent={"proposal": 12}), flags=["Deals without a company"])
    assert out.index("Data may explain a change") < out.index("Constraint")


# --- small samples and missing data ----------------------------------------------------------

def test_a_small_sample_names_no_constraint(tmp_path):
    db = make_db(tmp_path / "l.duckdb", recent={"qualified": 5, "discovery": 1, "proposal": 1, "negotiation": 0, "won": 0})
    assert "fewer than 20 qualified deals" in report(db) and "Constraint" not in report(db)


def test_too_few_mature_cohorts_names_no_constraint(tmp_path):
    db = make_db(tmp_path / "l.duckdb", as_of=date(2025, 11, 1))
    assert "No constraint is named" in report(db, today=date(2025, 11, 3))


def test_stale_data_stops_the_review(db):
    with pytest.raises(review.ReviewError, match="more than 7 days old"):
        report(db, today=date(2026, 2, 1))


def test_a_missing_lakehouse_or_table_stops_the_review(tmp_path):
    with pytest.raises(review.ReviewError, match="not found"):
        review.read_gold(tmp_path / "none.duckdb")
    other = tmp_path / "o.duckdb"
    con = duckdb.connect(str(other))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.funnel_stage_monthly (a INT)")
    con.close()
    with pytest.raises(review.ReviewError, match="cannot read"):
        review.read_gold(other)


# --- the audit of the same week --------------------------------------------------------------

def test_flags_come_from_the_audit_of_the_same_week(tmp_path):
    (tmp_path / "audit-2026-01-09.md").write_text(
        "**Attention, higher than the last report:** Deals without a company, Possible duplicate companies.\n", encoding="utf-8")
    assert review.audit_flags(tmp_path, AS_OF, TODAY) == ["Deals without a company", "Possible duplicate companies"]


def test_an_audit_that_raised_nothing_or_an_old_one_gives_no_flags(tmp_path):
    (tmp_path / "audit-2026-01-09.md").write_text("Nothing rose since the last report.\n", encoding="utf-8")
    (tmp_path / "audit-2025-06-01.md").write_text("**Attention, higher than the last report:** Old flag.\n", encoding="utf-8")
    assert review.audit_flags(tmp_path, AS_OF, TODAY) == []
    assert review.audit_flags(tmp_path / "missing", AS_OF, TODAY) == []


# --- the effect, the dry run and idempotency ------------------------------------------------

def run(tmp_path, db, *extra):
    return review.main(["--db", str(db), "--logs", str(tmp_path / "logs"), "--date", TODAY.isoformat(), *extra])


def test_dry_run_is_the_default_and_writes_nothing(tmp_path, db, capsys):
    assert run(tmp_path, db) == 0
    assert "dry run" in capsys.readouterr().out and not (tmp_path / "logs").exists()


def test_write_makes_one_file_per_data_date_and_a_second_run_changes_nothing(tmp_path, db):
    run(tmp_path, db, "--write")
    path = tmp_path / "logs" / "funnel-review-2026-01-09.md"
    first = path.read_text(encoding="utf-8")
    run(tmp_path, db, "--write")
    assert path.read_text(encoding="utf-8") == first and len(list((tmp_path / "logs").glob("*.md"))) == 1


def test_a_failed_run_exits_with_one_and_writes_nothing(tmp_path, capsys):
    assert run(tmp_path, tmp_path / "none.duckdb", "--write") == 1
    assert "ERROR" in capsys.readouterr().err and not (tmp_path / "logs").exists()


def test_the_script_only_reads_gold_and_has_no_way_to_write_or_send():
    code = (ROOT / "automations" / "funnel-review" / "review.py").read_text(encoding="utf-8").lower()
    assert "silver." not in code and "bronze." not in code and "read_only=true" in code
    assert not any(word in code for word in ("insert into", "update gold", "delete from", "drop table", "smtp", "requests.post"))
    assert all(f"gold.{t}" in (ROOT / "automations" / "funnel-review" / "SPEC.md").read_text(encoding="utf-8") for t in review.TABLES)
