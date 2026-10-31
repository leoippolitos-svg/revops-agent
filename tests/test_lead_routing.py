"""Tests for automations/lead-routing/route.py. A tiny hand-made gold table, not dbt."""

import importlib.util
import json
import shutil
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
# The folder name has a dash, so the module is loaded by path.
spec = importlib.util.spec_from_file_location("route_leads", ROOT / "automations" / "lead-routing" / "route.py")
route_leads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_leads)

OWNERS = [("s1", "sales", 15), ("s2", "sales", 19), ("s3", "sales", 30), ("e1", "enterprise", 3),
          ("e2", "enterprise", 8), ("c1", "customer_success", 0)]


def make_db(path: Path, owners=OWNERS) -> Path:
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.owner_workload (owner_id VARCHAR, team VARCHAR, open_deals INT, open_amount_usd INT)")
    for owner, team, deals in owners:
        con.execute("INSERT INTO gold.owner_workload VALUES (?, ?, ?, 0)", [owner, team, deals])
    con.close()
    return path


@pytest.fixture
def db(tmp_path):
    return make_db(tmp_path / "lake.duckdb")


def lead(lead_id="L1", company="C1", segment="mid_market", owner=None):
    return {"lead_id": lead_id, "company_id": company, "segment": segment, "owner_id": owner}


def decide(leads, db, rules=None):
    return route_leads.route(leads, route_leads.read_workload(db), rules or route_leads.load_rules())


# --- the rules come from the context document -------------------------------------------

def test_the_rules_are_read_from_the_document():
    rules = route_leads.load_rules()
    assert rules["limit"] == {"sales": 30, "enterprise": 8}
    assert rules["team_of"] == {"smb": "sales", "mid_market": "sales", "enterprise": "enterprise"}


def test_changing_the_document_changes_the_limit_with_no_code_change(tmp_path, db):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    doc = context / "concepts" / "lead-routing.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("30 for the sales team", "16 for the sales team"), encoding="utf-8")
    rules = route_leads.load_rules(context)
    assert rules["limit"]["sales"] == 16
    # s1 has 15 and takes L1 (now 16, the limit); s2 (19) was already over it, so L2 has nobody.
    first, second = decide([lead("L1"), lead("L2")], db, rules)
    assert first["owner_id"] == "s1" and second["outcome"] == "not routed"


def test_a_document_that_no_longer_says_the_limits_stops_the_run(tmp_path):
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    (context / "concepts" / "lead-routing.md").write_text("# Lead routing\n", encoding="utf-8")
    with pytest.raises(route_leads.RoutingError):
        route_leads.load_rules(context)


# --- the routing rules ------------------------------------------------------------------

def test_the_segment_picks_the_team_and_the_owner_with_the_fewest_open_deals(db):
    sales, enterprise = decide([lead(segment="smb"), lead("L2", segment="enterprise")], db)
    assert (sales["owner_id"], sales["rule"]) == ("s1", "fewest open deals")
    assert enterprise["owner_id"] == "e1"


def test_account_continuity_comes_before_the_fewest_open_deals(db):
    out = decide([lead(owner="s2")], db)[0]
    assert (out["owner_id"], out["rule"]) == ("s2", "account continuity")


def test_an_account_owner_in_the_wrong_team_does_not_count_as_continuity(db):
    assert decide([lead(owner="c1")], db)[0]["owner_id"] == "s1"
    assert decide([lead(segment="enterprise", owner="s1")], db)[0]["owner_id"] == "e1"


def test_an_account_owner_at_the_limit_still_gets_the_lead_within_the_tolerance(db):
    out = decide([lead(owner="s3")], db)[0]  # s3 has 30, the ceiling is 31 (5% over 30, rounded down)
    assert out["owner_id"] == "s3" and "within the tolerance" in out["rule"]


def test_the_owner_who_reached_the_ceiling_gets_no_more_and_a_person_decides(db):
    out = decide([lead("A", owner="s3"), lead("B", owner="s3")], db)  # the second would make 32
    assert out[0]["owner_id"] == "s3" and out[1]["outcome"] == "not routed" and "a person decides" in out[1]["rule"]


def test_an_enterprise_owner_has_no_tolerance_because_five_percent_of_eight_is_under_one_deal(db):
    out = decide([lead(segment="enterprise", owner="e2")], db)[0]  # e2 has 8, the ceiling is 8
    assert out["outcome"] == "not routed" and "ceiling of 8" in out["rule"]


def test_the_tolerance_is_read_from_the_document_and_a_wider_one_changes_the_ceiling(tmp_path, db):
    assert route_leads.load_rules()["tolerance_percent"] == 5
    context = tmp_path / "context"
    shutil.copytree(ROOT / "context", context)
    doc = context / "concepts" / "lead-routing.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("at most 5% over", "at most 20% over"), encoding="utf-8")
    rules = route_leads.load_rules(context)
    assert [d["owner_id"] for d in decide([lead("A", owner="s3"), lead("B", owner="s3")], db, rules)] == ["s3", "s3"]  # ceiling 36


def test_a_tie_goes_to_the_lowest_owner_id(tmp_path):
    db = make_db(tmp_path / "t.duckdb", [("s2", "sales", 4), ("s1", "sales", 4)])
    assert decide([lead()], db)[0]["owner_id"] == "s1"


def test_an_owner_at_the_limit_never_receives_a_lead_and_the_shortage_is_reported(tmp_path):
    db = make_db(tmp_path / "t.duckdb", [("e1", "enterprise", 8), ("e2", "enterprise", 8)])
    out = decide([lead(segment="enterprise")], db)[0]
    assert out["outcome"] == "not routed" and "shortage" in out["rule"] and out["owner_id"] == "-"


def test_teams_that_never_receive_leads_are_never_chosen(tmp_path):
    db = make_db(tmp_path / "t.duckdb", [("c1", "customer_success", 0), ("s1", "sales", 29)])
    assert decide([lead()], db)[0]["owner_id"] == "s1"


@pytest.mark.parametrize("event", [lead(company=None), lead(segment=None), lead(segment="galactic")])
def test_a_lead_with_no_company_or_no_known_segment_is_listed_not_routed(db, event):
    out = decide([event], db)[0]
    assert out["outcome"] == "not routed" and "cleanup" in out["rule"]


def test_a_batch_counts_each_assignment_so_two_leads_never_see_the_same_number(tmp_path):
    db = make_db(tmp_path / "t.duckdb", [("s1", "sales", 10), ("s2", "sales", 11)])
    owners = [d["owner_id"] for d in decide([lead("A"), lead("B"), lead("C")], db)]
    assert owners == ["s1", "s1", "s2"]  # 10 -> 11 ties with s2 and the lowest id wins; then s2 has the fewest


def test_the_same_input_always_gives_the_same_decisions(db):
    leads = [lead("A"), lead("B", segment="enterprise"), lead("C", owner="s2")]
    assert decide(leads, db) == decide(leads, db)


# --- failures stop the run ---------------------------------------------------------------

def test_a_missing_lakehouse_or_table_or_an_empty_table_stops_the_run(tmp_path):
    with pytest.raises(route_leads.RoutingError, match="not found"):
        route_leads.read_workload(tmp_path / "nope.duckdb")
    other = tmp_path / "o.duckdb"
    con = duckdb.connect(str(other))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.x (a INT)")
    con.close()
    with pytest.raises(route_leads.RoutingError, match="cannot read"):
        route_leads.read_workload(other)
    with pytest.raises(route_leads.RoutingError, match="empty"):
        route_leads.read_workload(make_db(tmp_path / "e.duckdb", []))


@pytest.mark.parametrize("leads", ["x", [1], [{"company_id": "C"}], [{"lead_id": " "}], [lead("A"), lead("A")]])
def test_bad_lead_events_are_refused(leads):
    with pytest.raises(route_leads.RoutingError):
        route_leads.check_leads(leads)


# --- the effect, the dry run and idempotency ---------------------------------------------

def run(tmp_path, db, leads, *extra):
    file = tmp_path / "leads.json"
    file.write_text(json.dumps(leads), encoding="utf-8")
    return route_leads.main(["--leads", str(file), "--db", str(db), "--logs", str(tmp_path / "logs"),
                             "--date", "2026-01-09", *extra])


def test_dry_run_is_the_default_and_writes_nothing(tmp_path, db, capsys):
    assert run(tmp_path, db, [lead()]) == 0
    assert "dry run" in capsys.readouterr().out and not (tmp_path / "logs").exists()


def test_write_makes_one_line_per_lead_and_a_second_run_changes_nothing(tmp_path, db):
    leads = [lead("A"), lead("B", segment="enterprise"), lead("C", company=None)]
    run(tmp_path, db, leads, "--write")
    log = tmp_path / "logs" / "lead-routing-2026-01-09.md"
    first = log.read_text(encoding="utf-8")
    run(tmp_path, db, leads, "--write")
    assert log.read_text(encoding="utf-8") == first
    assert len([row for row in first.splitlines() if row.startswith("| ") and "---" not in row]) == 4  # header + 3


def test_a_new_lead_is_added_without_touching_the_existing_lines(tmp_path, db):
    run(tmp_path, db, [lead("A")], "--write")
    run(tmp_path, db, [lead("B")], "--write")
    text = (tmp_path / "logs" / "lead-routing-2026-01-09.md").read_text(encoding="utf-8")
    assert "| A |" in text and "| B |" in text


def test_a_failed_run_exits_with_one_and_writes_nothing(tmp_path, capsys):
    assert run(tmp_path, tmp_path / "missing.duckdb", [lead()], "--write") == 1
    assert "ERROR" in capsys.readouterr().err and not (tmp_path / "logs").exists()


def test_the_report_counts_what_was_not_routed(tmp_path, db, capsys):
    run(tmp_path, db, [lead("A"), lead("B", company=None)])
    assert "1 assigned, 1 not routed." in capsys.readouterr().out


def test_the_automation_never_touches_silver_or_bronze_or_writes_to_gold():
    code = (ROOT / "automations" / "lead-routing" / "route.py").read_text(encoding="utf-8").lower()
    assert "silver." not in code and "bronze." not in code
    assert "from gold.owner_workload" in code and "read_only=true" in code
    assert not any(word in code for word in ("insert into", "update gold", "delete from", "drop table"))
