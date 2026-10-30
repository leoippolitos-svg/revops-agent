"""Check that the eval case files are well formed.

Run from the repository root:
    python tools/check_evals.py

This does not run the agent. It checks the case files themselves, so a typo in
an intent or a document id fails in CI instead of silently scoring zero later:

  1. retrieval_cases.yaml: at least 40 cases, every expected document is in
     context/index.yaml, and every document has at least one case.
  2. router_cases.yaml: at least 40 cases, every intent is one listed in
     agent/directives/routing.md, and every intent has at least one case.
  3. router_heldout.yaml: at least 20 cases with the same rules, and none of its
     questions is also in router_cases.yaml, or it would not be held out.
  4. No question appears twice in the same file.
  5. Every skill named in routing.md exists in agent/skills/.
"""

import re
import sys
from pathlib import Path

import yaml

MIN_CASES = 40
MIN_HELDOUT_CASES = 20


def load_cases(path: Path) -> list[dict]:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("cases", [])


def routing_intents(root: Path) -> set[str]:
    """Intents are the backticked first column of the table in routing.md."""
    text = (root / "agent" / "directives" / "routing.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| `([a-z_]+)` \|", text, flags=re.MULTILINE))


def check_file(root: Path, name: str, key: str, allowed: set[str], noun: str, minimum: int = MIN_CASES) -> list[str]:
    path = root / "evals" / name
    if not path.is_file():
        return [f"evals/{name}: file is missing"]
    cases = load_cases(path)
    errors = []
    if len(cases) < minimum:
        errors.append(f"evals/{name}: {len(cases)} cases, the minimum is {minimum}")
    seen = set()
    for number, case in enumerate(cases, start=1):
        question = (case.get("question") or "").strip()
        if not question:
            errors.append(f"evals/{name}: case {number} has no question")
        if question.lower() in seen:
            errors.append(f"evals/{name}: duplicated question {question!r}")
        seen.add(question.lower())
        if case.get(key) not in allowed:
            errors.append(f"evals/{name}: case {number} has unknown {noun} {case.get(key)!r}")
    for missing in sorted(allowed - {c.get(key) for c in cases}):
        errors.append(f"evals/{name}: no case covers the {noun} {missing!r}")
    return errors


def heldout_overlap(root: Path) -> list[str]:
    """A held-out question that is also a tuning question measures nothing."""
    path = root / "evals" / "router_heldout.yaml"
    if not path.is_file():
        return []
    tuning = {(c.get("question") or "").strip().lower() for c in load_cases(root / "evals" / "router_cases.yaml")}
    return [f"evals/router_heldout.yaml: {c['question']!r} is also in router_cases.yaml"
            for c in load_cases(path) if (c.get("question") or "").strip().lower() in tuning]


def routing_skills(root: Path) -> set[str]:
    """Skills are the last column of the routing table; a dash means none."""
    text = (root / "agent" / "directives" / "routing.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| `[a-z_]+` \|.*\| ([^|]+) \|\s*$", text, flags=re.MULTILINE)
    return {r.strip() for r in rows} - {"—"}


def skill_errors(root: Path) -> list[str]:
    """A routing rule that names a skill with no folder would send the agent nowhere."""
    return [f"agent/directives/routing.md: skill {name!r} has no folder in agent/skills/"
            for name in sorted(routing_skills(root))
            if not (root / "agent" / "skills" / name / "SKILL.md").is_file()]


def check(root: Path) -> list[str]:
    index = yaml.safe_load((root / "context" / "index.yaml").read_text(encoding="utf-8")) or {}
    documents = {c["id"] for c in index.get("concepts", []) if c.get("status") != "planned"}
    return (check_file(root, "retrieval_cases.yaml", "expected", documents, "document")
            + check_file(root, "router_cases.yaml", "intent", routing_intents(root), "intent")
            + check_file(root, "router_heldout.yaml", "intent", routing_intents(root), "intent", MIN_HELDOUT_CASES)
            + heldout_overlap(root)
            + skill_errors(root))


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked eval case files: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
