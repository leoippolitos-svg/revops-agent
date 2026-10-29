"""Tests for generator/generate.py (part 1: base entities)."""

import csv
import hashlib
import json
import sys
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
    for path in sorted(folder.rglob("*.csv")) + [folder / "_issues.json"]:
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
