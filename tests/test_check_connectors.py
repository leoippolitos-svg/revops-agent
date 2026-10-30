"""Tests for tools/check_connectors.py."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_connectors  # noqa: E402


def repo_with(tmp_path: Path, connectors: list[dict]) -> Path:
    (tmp_path / "connectors").mkdir()
    (tmp_path / "connectors" / "registry.yaml").write_text(
        yaml.safe_dump({"connectors": connectors}), encoding="utf-8")
    return tmp_path


def good(**changes) -> dict:
    entry = {"id": "demo", "system": "Demo", "status": "simulated", "access": "read",
             "scopes": ["one table"], "auth": "token in DEMO_TOKEN", "consumers": ["pipeline"], "owner": "RevOps"}
    return {**entry, **changes}


def test_the_real_registry_passes():
    assert check_connectors.check(ROOT) == []


def test_a_valid_entry_passes(tmp_path):
    assert check_connectors.check(repo_with(tmp_path, [good()])) == []


def test_missing_field_is_reported(tmp_path):
    entry = good()
    del entry["owner"]
    errors = check_connectors.check(repo_with(tmp_path, [entry]))
    assert any("missing owner" in e for e in errors)


def test_duplicate_id_is_reported(tmp_path):
    errors = check_connectors.check(repo_with(tmp_path, [good(), good()]))
    assert any("duplicated id" in e for e in errors)


def test_secret_in_auth_is_reported(tmp_path):
    # Built at run time so this file holds nothing shaped like a real key for scanners to flag.
    fake_key = "sk" + "-" + "x" * 20
    root = repo_with(tmp_path, [good(auth=fake_key)])
    assert any("looks like a secret" in e for e in check_connectors.check(root))


def test_read_write_rules(tmp_path):
    live = good(access="read-write", status="live", note="see ADR-0009")
    no_note = good(id="b", access="read-write", status="documented")
    agent = good(id="c", access="read-write", status="documented", note="ADR pending", consumers=["agent"])
    errors = check_connectors.check(repo_with(tmp_path, [live, no_note, agent]))
    assert any("cannot be live" in e for e in errors)
    assert any("needs a note that points to its ADR" in e for e in errors)
    assert any("must not consume a read-write connector" in e for e in errors)


def test_unknown_status_and_empty_scopes_are_reported(tmp_path):
    errors = check_connectors.check(repo_with(tmp_path, [good(status="maybe", scopes=[])]))
    assert any("status must be one of" in e for e in errors)
    assert any("missing scopes" in e for e in errors)
