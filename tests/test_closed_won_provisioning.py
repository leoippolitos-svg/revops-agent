"""Tests for automations/closed-won-provisioning/provision.py."""

import importlib.util
import json
import shutil
from datetime import date
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
# The folder name has dashes, so the module is loaded by path.
spec = importlib.util.spec_from_file_location(
    "provision_deals", ROOT / "automations" / "closed-won-provisioning" / "provision.py")
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)

TODAY = date(2026, 1, 20)


def deal(deal_id="D1", **overrides):
    base = {"deal_id": deal_id, "stage": "closed_won", "company_id": "C1",
            "company_is_possible_duplicate": False, "has_subscription": False}
    return base | overrides


def decide(**overrides):
    return provision.decide(deal(**overrides), provision.load_rules(), TODAY)


def make_db(path: Path, backlog=7) -> Path:
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.data_quality_snapshot (closed_won_without_subscription INT)")
    con.execute("INSERT INTO gold.data_quality_snapshot VALUES (?)", [backlog])
    con.close()
    return path

@pytest.fixture(autouse=True)
def kill_switch_on(monkeypatch):
    """Writes need the kill switch on; tests that check it is off unset it themselves."""
    monkeypatch.setenv("CLOSED_WON_PROVISIONING_ENABLED", "true")



# --- the rules come from the context document ---------------------------------------------

def test_the_rules_are_read_from_the_document():
    assert provision.load_rules() == {"wait_days": 14, "milestone": "kickoff", "cutoff_days": 60}


def test_changing_the_document_changes_the_wait_with_no_code_change(tmp_path):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    doc = context / "concepts" / "closed-won-provisioning.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("within two weeks", "within three weeks"), encoding="utf-8")
    assert provision.load_rules(context)["wait_days"] == 21


def test_a_document_that_no_longer_says_the_rules_stops_the_run(tmp_path):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    (context / "concepts" / "closed-won-provisioning.md").write_text("# x\n", encoding="utf-8")
    with pytest.raises(provision.ProvisioningError):
        provision.load_rules(context)


# --- the decision ---------------------------------------------------------------------------

def test_a_clean_closed_won_deal_gets_a_kickoff_request():
    assert decide() == ("requested", "kickoff requested")


@pytest.mark.parametrize("overrides, outcome, text", [
    ({"stage": "negotiation"}, "skipped", "not in closed_won"),
    ({"stage": None}, "skipped", "not in closed_won"),
    ({"company_id": None}, "needs review", "no company"),
    ({"company_id": ""}, "needs review", "no company"),
    ({"company_is_possible_duplicate": True}, "held", "possible duplicate"),
    ({"has_subscription": True}, "skipped", "already has a subscription"),
])
def test_a_deal_that_must_not_be_provisioned_is_skipped_or_held_with_a_reason(overrides, outcome, text):
    got_outcome, reason = decide(**overrides)
    assert got_outcome == outcome and text in reason


def test_a_missing_company_is_checked_before_the_duplicate_flag_and_the_subscription():
    assert decide(company_id=None, company_is_possible_duplicate=True, has_subscription=True)[1].startswith("no company")


def test_no_subscription_after_two_weeks_is_flagged_for_finance_but_still_requested():
    outcome, reason = decide(closed_won_at="2026-01-05")
    assert outcome == "requested" and "listed for Finance" in reason


def test_a_deal_inside_the_two_weeks_is_not_flagged():
    assert "Finance" not in decide(closed_won_at="2026-01-10")[1]


def test_a_bad_date_stops_the_run():
    with pytest.raises(provision.ProvisioningError):
        decide(closed_won_at="last tuesday")


def test_the_plan_and_the_price_are_never_part_of_a_decision():
    assert not any(k in deal() for k in ("plan", "price", "amount"))
    code = (ROOT / "automations" / "closed-won-provisioning" / "provision.py").read_text(encoding="utf-8").lower()
    assert "silver." not in code and "bronze." not in code
    assert not any(word in code for word in ("insert into", "update gold", "delete from", "drop table", "smtp", "requests.post"))


# --- events and failures ---------------------------------------------------------------------

def test_one_event_or_a_list_is_accepted():
    assert len(provision.check_deals(deal())) == 1
    assert len(provision.check_deals([deal("A"), deal("B")])) == 2


@pytest.mark.parametrize("deals", ["x", [1], {"stage": "closed_won"}, {"deal_id": " "}, [deal("A"), deal("A")]])
def test_a_bad_event_is_refused(deals):
    with pytest.raises(provision.ProvisioningError):
        provision.check_deals(deals)


# --- the effect, the dry run and idempotency -------------------------------------------------

def run(tmp_path, events, *extra, db=None):
    file = tmp_path / "deals.json"
    file.write_text(json.dumps(events), encoding="utf-8")
    return provision.main(["--deals", str(file), "--db", str(db or tmp_path / "none.duckdb"),
                           "--logs", str(tmp_path / "logs"), "--date", "2026-01-20", *extra])


def test_dry_run_is_the_default_and_writes_nothing(tmp_path, capsys):
    assert run(tmp_path, deal()) == 0
    assert "dry run" in capsys.readouterr().out and not (tmp_path / "logs").exists()


def test_write_makes_one_line_per_deal_and_a_second_run_changes_nothing(tmp_path):
    events = [deal("A"), deal("B", company_id=None), deal("C", company_is_possible_duplicate=True)]
    run(tmp_path, events, "--write")
    log = tmp_path / "logs" / "provisioning-2026-01-20.md"
    first = log.read_text(encoding="utf-8")
    run(tmp_path, events, "--write")
    assert log.read_text(encoding="utf-8") == first
    assert first.count("\n| ") == 3 + 1  # the table header row and three deals


def test_a_deal_that_changes_outcome_replaces_its_own_line_only(tmp_path):
    run(tmp_path, [deal("A"), deal("B")], "--write")
    run(tmp_path, deal("A", has_subscription=True), "--write")
    text = (tmp_path / "logs" / "provisioning-2026-01-20.md").read_text(encoding="utf-8")
    assert "| A | skipped |" in text and "| B | requested |" in text and text.count("| A |") == 1


def test_a_bad_event_exits_with_one_and_requests_nothing(tmp_path, capsys):
    assert run(tmp_path, {"stage": "closed_won"}, "--write") == 1
    assert "ERROR" in capsys.readouterr().err and not (tmp_path / "logs").exists()


def test_the_backlog_figure_comes_from_the_snapshot(tmp_path, capsys):
    run(tmp_path, deal(), db=make_db(tmp_path / "lake.duckdb", backlog=7))
    assert "backlog without a subscription: 7." in capsys.readouterr().out


def test_a_missing_snapshot_still_handles_the_deal_and_says_the_figure_is_unavailable(tmp_path, capsys):
    other = tmp_path / "o.duckdb"
    con = duckdb.connect(str(other))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.x (a INT)")
    con.close()
    for db in (tmp_path / "missing.duckdb", other):
        assert run(tmp_path, deal(), db=db) == 0
        out = capsys.readouterr().out
        assert "1 requested" in out and "unavailable" in out
