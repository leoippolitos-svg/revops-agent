"""Check that connectors/registry.yaml follows docs/standards/connectors.md.

Run from the repository root:
    python tools/check_connectors.py

It exits with code 1 if any rule is broken:

  1. Every entry has all the required fields, and ids are unique.
  2. status is live, simulated or documented. access is read or read-write.
  3. scopes is a non-empty list, so nothing is registered as "everything".
  4. auth names a method or a variable, never a secret value.
  5. A read-write connector is never live, and has a note that points to its
     ADR (docs/standards/connectors.md: write access needs an ADR).
  6. The agent and the MCP server never consume a read-write connector
     (docs/standards/security.md: the agent advises, it does not execute).
"""

import re
import sys
from pathlib import Path

import yaml

REQUIRED = ("id", "system", "status", "access", "scopes", "auth", "consumers", "owner")
STATUSES = {"live", "simulated", "documented"}
ACCESS = {"read", "read-write"}
# Consumers that must stay read-only, whatever the connector says.
READ_ONLY_CONSUMERS = {"agent", "mcp_server"}
# Shapes of real keys and tokens. A long unbroken string is also suspicious.
SECRET_SHAPE = re.compile(r"(sk-[A-Za-z0-9]|ghp_|xox[bp]-|AKIA[0-9A-Z]{8}|[A-Za-z0-9+/_-]{32,})")


def check(root: Path) -> list[str]:
    data = yaml.safe_load((root / "connectors" / "registry.yaml").read_text(encoding="utf-8")) or {}
    errors, seen = [], set()
    for number, entry in enumerate(data.get("connectors", []), start=1):
        name = entry.get("id", f"entry {number}")
        where = f"connectors/registry.yaml: {name}"
        for field in REQUIRED:
            if entry.get(field) in (None, "", []):
                errors.append(f"{where}: missing {field}")
        if name in seen:
            errors.append(f"{where}: duplicated id")
        seen.add(name)
        if entry.get("status") not in STATUSES:
            errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if entry.get("access") not in ACCESS:
            errors.append(f"{where}: access must be one of {sorted(ACCESS)}")
        if not isinstance(entry.get("scopes"), list):
            errors.append(f"{where}: scopes must be a list")
        if SECRET_SHAPE.search(str(entry.get("auth", ""))):
            errors.append(f"{where}: auth looks like a secret; name the method or the variable only")
        if entry.get("access") == "read-write":
            if entry.get("status") == "live":
                errors.append(f"{where}: a read-write connector cannot be live without an ADR-backed change")
            if "adr" not in str(entry.get("note", "")).lower():
                errors.append(f"{where}: read-write needs a note that points to its ADR")
            bad = READ_ONLY_CONSUMERS & set(entry.get("consumers") or [])
            if bad:
                errors.append(f"{where}: {sorted(bad)} must not consume a read-write connector")
    return errors


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked the connector registry: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
