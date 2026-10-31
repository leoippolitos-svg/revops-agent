"""Tests for tools/check_pii.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_pii  # noqa: E402


def test_the_repository_has_no_personal_data():
    assert check_pii.check(ROOT) == []


def test_a_real_looking_email_or_phone_is_found_and_fictional_ones_pass():
    # The samples are split in the source so this file does not trip the scan it tests.
    text = ("contact jane.doe" + "@" + "realcompany.io\n"
            "call +44 20 " + "7946 0958\n"
            "dana@example.com and <email> are fine\n"
            "the metadata host 169.254.169.254 is not a phone\n"
            "Co-Authored-By: Claude <noreply@anthropic.com>\n")
    assert check_pii.scan_text(text) == [1, 2]
