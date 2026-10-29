"""Tests for generator/generate.py and generator/billing_cs.py."""

import csv
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# The generator is a script, not an installed package, so we add its folder to
# the import path to be able to `import generate`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generator"))

import generate  # noqa: E402


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_issues(folder: Path) -> list[dict]:
    return json.loads((folder / "_issues.json").read_text(encoding="utf-8"))


def folder_hash(folder: Path) -> str:
    """One hash for every file in a folder, so we can compare two runs."""
    digest = hashlib.sha256()
    extra = [folder / "_issues.json"] if (folder / "_issues.json").is_file() else []
    for path in sorted(folder.rglob("*.csv")) + extra:
        digest.update(path.relative_to(folder).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_same_seed_gives_identical_files(tmp_path):
    generate.generate(seed=7, out_dir=tmp_path / "a")
    generate.generate(seed=7, out_dir=tmp_path / "b")
    assert folder_hash(tmp_path / "a") == folder_hash(tmp_path / "b")


def test_different_seed_gives_different_files(tmp_path):
    generate.generate(seed=1, out_dir=tmp_path / "a")
    generate.generate(seed=2, out_dir=tmp_path / "b")
    assert folder_hash(tmp_path / "a") != folder_hash(tmp_path / "b")


def test_row_counts(tmp_path):
    counts = generate.generate(seed=42, out_dir=tmp_path)
    duplicates = len(issue_ids(tmp_path, "duplicate_company"))
    assert counts["companies"] == generate.COMPANY_COUNT + duplicates
    assert counts["contacts"] == generate.CONTACT_COUNT
    assert counts["owners"] == sum(n for _, n in generate.OWNER_TEAMS)


def test_every_contact_points_to_an_existing_company(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    company_ids = {r["company_id"] for r in read_rows(tmp_path / "crm" / "companies.csv")}
    contacts = read_rows(tmp_path / "crm" / "contacts.csv")
    assert all(c["company_id"] in company_ids for c in contacts)


def test_every_company_has_an_existing_owner_of_the_right_team(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    owners = {r["owner_id"]: r["team"] for r in read_rows(tmp_path / "crm" / "owners.csv")}
    for company in read_rows(tmp_path / "crm" / "companies.csv"):
        team = owners[company["owner_id"]]
        expected = "enterprise" if company["segment"] == "enterprise" else "sales"
        assert team == expected


def test_primary_keys_are_unique(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    keys = {
        "crm/owners.csv": "owner_id",
        "crm/companies.csv": "company_id",
        "crm/contacts.csv": "contact_id",
        "marketing/campaigns.csv": "campaign_id",
        "crm/deals.csv": "deal_id",
        "crm/deal_stage_history.csv": "history_id",
        "marketing/form_submissions.csv": "submission_id",
        "billing/subscriptions.csv": "subscription_id",
        "billing/invoices.csv": "invoice_id",
        "billing/payments.csv": "payment_id",
        "cs/onboarding_milestones.csv": "milestone_id",
        "cs/health_scores.csv": "score_id",
        "cs/tickets.csv": "ticket_id",
    }
    for file_name, key in keys.items():
        values = [r[key] for r in read_rows(tmp_path / file_name)]
        assert len(values) == len(set(values)), file_name


def test_company_names_are_unique_except_the_injected_duplicates(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    duplicate_ids = {str(i["row_id"]) for i in read_issues(tmp_path)
                     if i["type"] == "duplicate_company"}
    names = [r["name"].lower() for r in read_rows(tmp_path / "crm" / "companies.csv")
             if r["company_id"] not in duplicate_ids]
    assert len(names) == len(set(names))


def test_segment_matches_headcount(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    ranges = {name: (low, high) for name, low, high in generate.SEGMENTS}
    for company in read_rows(tmp_path / "crm" / "companies.csv"):
        low, high = ranges[company["segment"]]
        assert low <= int(company["employee_count"]) <= high


def test_contact_is_not_created_before_its_company(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    created = {r["company_id"]: r["created_at"]
               for r in read_rows(tmp_path / "crm" / "companies.csv")}
    for contact in read_rows(tmp_path / "crm" / "contacts.csv"):
        # ISO dates compare correctly as plain strings.
        assert contact["created_at"] >= created[contact["company_id"]]


def test_all_emails_use_the_reserved_example_domain(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    for file_name in ("crm/owners.csv", "crm/contacts.csv"):
        for row in read_rows(tmp_path / file_name):
            assert row["email"].endswith("@example.com")


# --- Deals, stage history, form submissions and the injected issues -----------

def issue_ids(folder: Path, kind: str) -> set[str]:
    return {str(i["row_id"]) for i in read_issues(folder) if i["type"] == kind}


def test_every_issue_type_is_injected_at_least_once(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    found = {i["type"] for i in read_issues(tmp_path)}
    assert found == set(generate.ISSUE_RATES)


def test_deals_without_company_are_exactly_the_planned_ones(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    empty = {d["deal_id"] for d in read_rows(tmp_path / "crm" / "deals.csv")
             if d["company_id"] == ""}
    assert empty == issue_ids(tmp_path, "deal_without_company")


def test_other_deals_point_to_an_existing_company(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    company_ids = {c["company_id"] for c in read_rows(tmp_path / "crm" / "companies.csv")}
    for deal in read_rows(tmp_path / "crm" / "deals.csv"):
        assert deal["company_id"] == "" or deal["company_id"] in company_ids


def test_stage_dates_are_in_order_except_the_planned_deals(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    by_deal = {}
    for row in read_rows(tmp_path / "crm" / "deal_stage_history.csv"):
        by_deal.setdefault(row["deal_id"], []).append(row["entered_at"])
    broken = {deal for deal, dates in by_deal.items() if dates != sorted(dates)}
    assert broken == issue_ids(tmp_path, "stage_dates_out_of_order")


def test_deal_current_stage_is_its_last_stage_and_closed_at_matches(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    last = {}
    for row in read_rows(tmp_path / "crm" / "deal_stage_history.csv"):
        last[row["deal_id"]] = row  # rows are in order, so the last one wins
    for deal in read_rows(tmp_path / "crm" / "deals.csv"):
        final = last[deal["deal_id"]]
        assert deal["stage"] == final["stage"]
        closed = final["stage"] in (generate.WON, generate.LOST)
        assert deal["closed_at"] == (final["entered_at"] if closed else "")


def test_mql_flags_disagree_exactly_for_the_planned_contacts(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    marketing = {s["contact_id"]: s["marketing_mql_flag"]
                 for s in read_rows(tmp_path / "marketing" / "form_submissions.csv")}
    conflicts = {c["contact_id"] for c in read_rows(tmp_path / "crm" / "contacts.csv")
                 if c["contact_id"] in marketing
                 and c["sales_mql_flag"] != marketing[c["contact_id"]]}
    assert conflicts == issue_ids(tmp_path, "mql_flag_conflict")


def test_form_submissions_reference_existing_contacts_and_campaigns(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    contacts = {c["contact_id"] for c in read_rows(tmp_path / "crm" / "contacts.csv")}
    campaigns = {c["campaign_id"] for c in read_rows(tmp_path / "marketing" / "campaigns.csv")}
    for row in read_rows(tmp_path / "marketing" / "form_submissions.csv"):
        assert row["contact_id"] in contacts and row["campaign_id"] in campaigns


def test_companies_minus_injected_duplicates_is_the_clean_count(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    companies = read_rows(tmp_path / "crm" / "companies.csv")
    clean = [c for c in companies if str(c["company_id"]) not in issue_ids(tmp_path, "duplicate_company")]
    assert len(clean) == generate.COMPANY_COUNT


# --- Billing and Customer Success ---------------------------------------------

def test_one_subscription_per_won_deal(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    won = [d for d in read_rows(tmp_path / "crm" / "deals.csv") if d["stage"] == generate.WON]
    subscriptions = read_rows(tmp_path / "billing" / "subscriptions.csv")
    assert len(subscriptions) == len(won)


def test_subscriptions_without_a_deal_are_exactly_the_planned_ones(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    deal_ids = {d["deal_id"] for d in read_rows(tmp_path / "crm" / "deals.csv")}
    orphans = {s["subscription_id"] for s in read_rows(tmp_path / "billing" / "subscriptions.csv")
               if s["deal_id"] not in deal_ids}
    assert orphans == issue_ids(tmp_path, "subscription_without_deal")


def test_subscriptions_always_have_a_company(tmp_path):
    # The deal may lose its company (an issue); the subscription never does.
    generate.generate(seed=42, out_dir=tmp_path)
    company_ids = {c["company_id"] for c in read_rows(tmp_path / "crm" / "companies.csv")}
    for sub in read_rows(tmp_path / "billing" / "subscriptions.csv"):
        assert sub["company_id"] in company_ids


def test_churned_subscriptions_have_an_end_date_and_active_ones_do_not(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    subscriptions = read_rows(tmp_path / "billing" / "subscriptions.csv")
    assert {s["status"] for s in subscriptions} == {"active", "churned"}
    for sub in subscriptions:
        if sub["status"] == "churned":
            assert sub["ended_at"] > sub["started_at"]
        else:
            assert sub["ended_at"] == ""


def test_invoices_reference_subscriptions_and_stop_when_the_subscription_ends(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    subs = {s["subscription_id"]: s for s in read_rows(tmp_path / "billing" / "subscriptions.csv")}
    for invoice in read_rows(tmp_path / "billing" / "invoices.csv"):
        sub = subs[invoice["subscription_id"]]
        assert invoice["issued_at"] >= sub["started_at"]
        assert sub["ended_at"] == "" or invoice["issued_at"] <= sub["ended_at"]
        assert invoice["amount_usd"] == sub["mrr_usd"]


def test_only_paid_invoices_have_exactly_one_payment_of_the_same_amount(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    invoices = {i["invoice_id"]: i for i in read_rows(tmp_path / "billing" / "invoices.csv")}
    payments = read_rows(tmp_path / "billing" / "payments.csv")
    paid_ids = [p["invoice_id"] for p in payments]
    assert len(paid_ids) == len(set(paid_ids))
    assert set(paid_ids) == {i for i, inv in invoices.items() if inv["status"] == "paid"}
    for payment in payments:
        assert payment["amount_usd"] == invoices[payment["invoice_id"]]["amount_usd"]
        assert payment["paid_at"] >= invoices[payment["invoice_id"]]["issued_at"]


def test_invoice_statuses_are_consistent_with_the_end_of_the_world(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    end = generate.billing_cs.WORLD_END.isoformat()
    statuses = set()
    for invoice in read_rows(tmp_path / "billing" / "invoices.csv"):
        statuses.add(invoice["status"])
        assert invoice["issued_at"] <= end
        # Open means not due yet; everything due by the end is paid or overdue.
        assert (invoice["status"] == "open") == (invoice["due_at"] > end)
    assert statuses == {"paid", "overdue", "open"}


def test_nothing_happens_after_the_end_of_the_world(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    end = generate.billing_cs.WORLD_END.isoformat()
    date_columns = {
        "billing/payments.csv": "paid_at",
        "cs/health_scores.csv": "scored_at",
        "cs/tickets.csv": "opened_at",
        "cs/onboarding_milestones.csv": "reached_at",
    }
    for file_name, column in date_columns.items():
        for row in read_rows(tmp_path / file_name):
            assert row[column] <= end, file_name


def test_health_score_band_matches_the_score(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    for row in read_rows(tmp_path / "cs" / "health_scores.csv"):
        score = int(row["score"])
        assert 0 <= score <= 100
        assert row["band"] == ("red" if score < 40 else "yellow" if score < 70 else "green")


def test_onboarding_milestones_follow_their_order(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    by_sub = {}
    for row in read_rows(tmp_path / "cs" / "onboarding_milestones.csv"):
        by_sub.setdefault(row["subscription_id"], []).append(row)
    for rows in by_sub.values():
        names = [r["milestone"] for r in rows]
        assert names == generate.billing_cs.MILESTONES[: len(names)]
        dates = [r["reached_at"] for r in rows]
        assert dates == sorted(dates)


def test_tickets_close_after_they_open(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path)
    tickets = read_rows(tmp_path / "cs" / "tickets.csv")
    assert tickets
    for ticket in tickets:
        assert ticket["closed_at"] == "" or ticket["closed_at"] >= ticket["opened_at"]


# --- Simulated time: snapshots as of a day, and --days ---------------------------

# One id column per table, used to follow rows from one day to the next.
KEYS = {
    "crm/companies": "company_id", "crm/contacts": "contact_id", "crm/deals": "deal_id",
    "crm/deal_stage_history": "history_id", "marketing/form_submissions": "submission_id",
    "billing/subscriptions": "subscription_id", "billing/invoices": "invoice_id",
    "billing/payments": "payment_id", "cs/onboarding_milestones": "milestone_id",
    "cs/health_scores": "score_id", "cs/tickets": "ticket_id",
}
DAY = date(2025, 9, 30)


def ids(folder: Path, name: str) -> set[str]:
    return {r[KEYS[name]] for r in read_rows(folder / f"{name}.csv")}


def test_a_snapshot_has_no_row_dated_after_its_day(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path, as_of=DAY)
    for name, column in generate.EXISTS_FROM.items():
        for row in read_rows(tmp_path / f"{name}.csv"):
            assert row[column] <= DAY.isoformat(), name


def test_an_early_snapshot_still_writes_every_file_with_its_header(tmp_path):
    # Before the first subscription exists some tables are empty, not missing.
    generate.generate(seed=42, out_dir=tmp_path, as_of=date(2025, 1, 2))
    assert (tmp_path / "billing" / "subscriptions.csv").read_text().startswith("subscription_id,")
    assert read_rows(tmp_path / "billing" / "subscriptions.csv") == []


def test_later_snapshots_only_add_rows(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path / "a", as_of=DAY)
    generate.generate(seed=42, out_dir=tmp_path / "b", as_of=DAY + timedelta(days=45))
    for name in KEYS:
        assert ids(tmp_path / "a", name) <= ids(tmp_path / "b", name), name


def test_references_hold_in_a_snapshot_taken_mid_way(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path, as_of=DAY)
    companies = ids(tmp_path, "crm/companies")
    deals = ids(tmp_path, "crm/deals")
    subs = ids(tmp_path, "billing/subscriptions")
    invoices = ids(tmp_path, "billing/invoices")
    assert all(r["company_id"] in companies for r in read_rows(tmp_path / "crm" / "contacts.csv"))
    assert all(r["company_id"] == "" or r["company_id"] in companies
               for r in read_rows(tmp_path / "crm" / "deals.csv"))
    assert all(r["deal_id"] in deals for r in read_rows(tmp_path / "crm" / "deal_stage_history.csv"))
    assert all(r["subscription_id"] in subs for r in read_rows(tmp_path / "billing" / "invoices.csv"))
    assert all(r["invoice_id"] in invoices for r in read_rows(tmp_path / "billing" / "payments.csv"))
    assert all(r["company_id"] in companies for r in read_rows(tmp_path / "billing" / "subscriptions.csv"))


def test_deal_stage_is_the_last_stage_seen_so_far(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path, as_of=DAY)
    last = {}
    for row in read_rows(tmp_path / "crm" / "deal_stage_history.csv"):
        last[row["deal_id"]] = row
    deals = read_rows(tmp_path / "crm" / "deals.csv")
    assert any(d["closed_at"] == "" for d in deals) and any(d["closed_at"] != "" for d in deals)
    for deal in deals:
        assert deal["stage"] == last[deal["deal_id"]]["stage"]
        closed = deal["stage"] in (generate.WON, generate.LOST)
        assert (deal["closed_at"] != "") == closed


def test_invoice_status_follows_payments_and_due_dates(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path, as_of=DAY)
    paid = {p["invoice_id"] for p in read_rows(tmp_path / "billing" / "payments.csv")}
    for invoice in read_rows(tmp_path / "billing" / "invoices.csv"):
        if invoice["invoice_id"] in paid:
            assert invoice["status"] == "paid"
        elif invoice["due_at"] > DAY.isoformat():
            assert invoice["status"] == "open"
        else:
            assert invoice["status"] == "overdue"


def test_churn_only_shows_once_its_date_is_reached(tmp_path):
    generate.generate(seed=42, out_dir=tmp_path, as_of=DAY)
    for sub in read_rows(tmp_path / "billing" / "subscriptions.csv"):
        if sub["status"] == "churned":
            assert sub["ended_at"] <= DAY.isoformat()
        else:
            assert sub["ended_at"] == ""


def test_days_writes_the_initial_load_then_one_folder_per_day(tmp_path):
    first = generate.generate_days(seed=42, out_dir=tmp_path, days=2)
    assert first == [generate.INITIAL_AS_OF,
                     generate.INITIAL_AS_OF + timedelta(days=1),
                     generate.INITIAL_AS_OF + timedelta(days=2)]
    # A second run continues after the latest day instead of starting again.
    second = generate.generate_days(seed=42, out_dir=tmp_path, days=1)
    assert second == [generate.INITIAL_AS_OF + timedelta(days=3)]
    folders = sorted(p.name for p in tmp_path.glob("as_of=*"))
    assert folders == [f"as_of={d.isoformat()}" for d in first + second]
    assert (tmp_path / "_issues.json").is_file()


def test_the_same_days_give_identical_files(tmp_path):
    generate.generate_days(seed=42, out_dir=tmp_path / "a", days=2)
    generate.generate_days(seed=42, out_dir=tmp_path / "b", days=2)
    assert folder_hash(tmp_path / "a") == folder_hash(tmp_path / "b")


def test_adding_days_never_changes_a_day_already_written(tmp_path):
    generate.generate_days(seed=42, out_dir=tmp_path / "a", days=1)
    generate.generate_days(seed=42, out_dir=tmp_path / "b", days=3)
    day = f"as_of={(generate.INITIAL_AS_OF + timedelta(days=1)).isoformat()}"
    assert folder_hash(tmp_path / "a" / day) == folder_hash(tmp_path / "b" / day)
