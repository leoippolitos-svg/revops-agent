"""Build the whole local lakehouse with one command.

Run from the repository root, after `pip install -r requirements.txt`:
    python tools/setup.py          # or: make setup

It runs, in order: generate fictional data (the initial load plus a few days),
load it into bronze, build silver and gold with dbt, then run the repository
and data checks. Everything is local, with no cloud account. It stops at the
first step that fails.

This is a Python script and not only a Makefile so it also works on Windows,
where `make` is usually not installed.
"""

import os
import subprocess
import sys
from pathlib import Path

DAYS = "3"  # initial load plus this many days, enough to see data change

STEPS = [
    ("Generate fictional data", [sys.executable, "generator/generate.py", "--days", DAYS]),
    ("Load into bronze", [sys.executable, "pipeline/ingest.py"]),
    # dbt reads dbt_project.yml and profiles.yml from its own folder.
    ("Build silver and gold", [sys.executable, "-c", "from dbt.cli.main import cli; cli()", "build",
                               "--project-dir", "pipeline/dbt", "--profiles-dir", "pipeline/dbt"]),
    ("Daily data check", [sys.executable, "pipeline/checks/daily_check.py"]),
    ("Context and catalog check", [sys.executable, "tools/check_context.py"]),
    ("Catalog page check", [sys.executable, "tools/build_catalog.py", "--check"]),
    ("Skills check", [sys.executable, "tools/check_skills.py"]),
]


def main() -> int:
    # dbt resolves a relative database path from the folder it runs in, so we hand
    # every step the same absolute path to the one lakehouse file.
    env = dict(os.environ, LAKEHOUSE_PATH=str(Path("data/lakehouse.duckdb").resolve()))
    for number, (title, command) in enumerate(STEPS, start=1):
        print(f"\n[{number}/{len(STEPS)}] {title}", flush=True)
        if subprocess.run(command, env=env).returncode != 0:
            print(f"\nStopped: step {number} ({title}) failed.")
            return 1
    print("\nDone. The lakehouse is in data/lakehouse.duckdb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
