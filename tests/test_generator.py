"""Tests for generator/generate.py (part 1: base entities)."""

import csv
import hashlib
import sys
from pathlib import Path

# The generator is a script, not an installed package, so we add its folder to
# the import path to be able to `import generate`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generator"))

import generate  # noqa: E402


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def folder_hash(folder: Path) -> str:
    """One hash for every file in a folder, so we can compare two runs."""
    digest = hashlib.sha256()
    for path in sorted(folder.rglob("*.csv")):
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
    assert counts["companies"] == generate.COMPANY_COUNT
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
    }
    for file_name, key in keys.items():
        values = [r[key] for r in read_rows(tmp_path / file_name)]
        assert len(values) == len(set(values)), file_name


def test_company_names_are_unique_in_part_one(tmp_path):
    # Duplicates are injected on purpose later; none should exist yet.
    generate.generate(seed=42, out_dir=tmp_path)
    names = [r["name"] for r in read_rows(tmp_path / "crm" / "companies.csv")]
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
