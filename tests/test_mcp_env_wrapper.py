"""Tests for tools/mcp_env_wrapper.py, with a temporary .env file (never the real one)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mcp_env_wrapper  # noqa: E402


def test_the_parser_reads_key_values_and_ignores_comments_and_lines_without_equals():
    text = "# comment\nA=1\nexport B='two'\nnot a pair\nC=\"three\"\n\n"
    assert mcp_env_wrapper.parse_env(text) == {"A": "1", "B": "two", "C": "three"}


def test_only_the_names_asked_for_are_added(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("WANTED=yes\nOTHER=no\n", encoding="utf-8")
    env = mcp_env_wrapper.build_env(env_file, ["WANTED"], {"PATH": "/bin"})
    assert env["WANTED"] == "yes" and "OTHER" not in env and env["PATH"] == "/bin"


def test_a_missing_name_stops_and_names_the_variable_not_a_value(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_VALUE_XYZ=abc\n", encoding="utf-8")
    with pytest.raises(SystemExit) as stop:
        mcp_env_wrapper.build_env(env_file, ["NEEDED"], {})
    assert "NEEDED" in str(stop.value) and "abc" not in str(stop.value)


def test_the_command_runs_without_a_shell_with_the_variable_set(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("WRAPPED=ok\n", encoding="utf-8")
    code = mcp_env_wrapper.main(["--env-file", str(env_file), "--need", "WRAPPED", "--",
                                 sys.executable, "-c", "import os,sys; sys.exit(0 if os.environ['WRAPPED']=='ok' else 3)"])
    assert code == 0


def test_the_template_holds_no_literal_secret():
    text = (ROOT / "mcp.template.json").read_text(encoding="utf-8")
    data = json.loads(text)
    for server in data["mcpServers"].values():
        for value in server.get("env", {}).values():
            assert value.startswith("${env:")
    assert "ghp_" not in text and "sk-" not in text
