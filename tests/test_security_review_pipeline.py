"""Tests for tools/security_review_eval.py and tools/push_scan.py, in both directions."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import push_scan  # noqa: E402
import security_review_eval  # noqa: E402


def write(tmp_path, findings):
    path = tmp_path / "results.json"
    path.write_text(json.dumps({"findings": findings}), encoding="utf-8")
    return path


def test_no_finding_is_green_and_says_green_is_not_a_full_review(tmp_path):
    assert security_review_eval.main([str(write(tmp_path, []))]) == 0
    assert "not a full review" in security_review_eval.decide([])[1]


def test_medium_and_low_are_listed_but_do_not_block(tmp_path):
    findings = [{"severity": "MEDIUM", "file": "a.py", "line": 3, "description": "x"}, {"severity": "low"}]
    assert security_review_eval.main([str(write(tmp_path, findings))]) == 0


@pytest.mark.parametrize("severity", ["HIGH", "CRITICAL", "high"])
def test_high_or_critical_turns_the_check_red(tmp_path, severity):
    findings = [{"severity": severity, "file": "app.py", "line": 10, "description": "SQL built from input"}]
    assert security_review_eval.main([str(write(tmp_path, findings))]) == 1


def test_a_missing_findings_file_is_a_failure_not_a_pass(tmp_path):
    assert security_review_eval.main([str(tmp_path / "none.json")]) == 1


def diff_adding(path, line):
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -0,0 +1 @@\n+{line}\n"


def test_a_clean_diff_passes():
    assert push_scan.scan(diff_adding("app.py", "print('hello')")) == []


@pytest.mark.parametrize("planted, kind", [
    # Built at run time, so no literal credential shape sits in this file for the secret scanners.
    ("AKIA" + "Q" * 16, "AWS access key"),
    ("gh" + "p_" + "a" * 36, "GitHub token"),
    ("sk-" + "ant-" + "b" * 24, "Anthropic key"),
    ("-----BEGIN " + "PRIVATE KEY-----", "private key block"),
    ("postgres://app:" + "s3cretpw" + "@db.internal/main", "connection string with a password"),
])
def test_a_planted_secret_is_found_and_only_its_kind_is_printed(planted, kind):
    hits = push_scan.scan(diff_adding("config.py", f"KEY = '{planted}'"))
    assert hits == [f"config.py: looks like a {kind}"] and planted not in hits[0]


def test_removed_lines_are_not_scanned():
    diff = "--- a/x.py\n+++ b/x.py\n@@ -1 +0,0 @@\n-" + "AKIA" + "Q" * 16 + "\n"
    assert push_scan.scan(diff) == []
