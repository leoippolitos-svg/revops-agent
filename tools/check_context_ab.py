"""Check the with-context vs without-context eval design in evals/context_ab/.

Run from the repository root:
    python tools/check_context_ab.py

It does not run the comparison. It checks that the questions are well formed and
that the results file never claims a number that was not measured:

  1. Question ids are unique, and every question has text, a trap and at least
     two checklist items (must_include).
  2. Every context_doc is a real document in context/index.yaml, and every
     canonical document has at least one question.
  3. Every row of results.md is either "not run" with no scores, or has two
     scores between 0 and 1.
"""

import re
import sys
from pathlib import Path

import yaml

MIN_ITEMS = 2


def check_questions(root: Path, documents: set[str]) -> list[str]:
    path = root / "evals" / "context_ab" / "questions.yaml"
    if not path.is_file():
        return ["evals/context_ab/questions.yaml: file is missing"]
    questions = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("questions", [])
    errors, seen = [], set()
    for number, q in enumerate(questions, start=1):
        name = q.get("id") or f"question {number}"
        where = f"evals/context_ab/questions.yaml: {name}"
        if name in seen:
            errors.append(f"{where}: duplicated id")
        seen.add(name)
        for field in ("question", "trap"):
            if not str(q.get(field) or "").strip():
                errors.append(f"{where}: missing {field}")
        if len(q.get("must_include") or []) < MIN_ITEMS:
            errors.append(f"{where}: needs at least {MIN_ITEMS} must_include items")
        if q.get("context_doc") not in documents:
            errors.append(f"{where}: unknown context_doc {q.get('context_doc')!r}")
    for missing in sorted(documents - {q.get("context_doc") for q in questions}):
        errors.append(f"evals/context_ab/questions.yaml: no question depends on the document {missing!r}")
    return errors


def check_results(root: Path) -> list[str]:
    path = root / "evals" / "context_ab" / "results.md"
    if not path.is_file():
        return ["evals/context_ab/results.md: file is missing"]
    errors = []
    for line in path.read_text(encoding="utf-8").splitlines():
        # A data row of the table: starts with a pipe and is not the header or the divider.
        if not line.startswith("|") or line.startswith("| Date") or set(line) <= set("|- "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        status, scores = cells[-1], cells[-3:-1]
        if status == "not run":
            if any(re.fullmatch(r"[0-9.]+", s) for s in scores):
                errors.append(f"evals/context_ab/results.md: a 'not run' row has a score: {line}")
        else:
            for s in scores:
                if not re.fullmatch(r"(0(\.\d+)?|1(\.0+)?)", s):
                    errors.append(f"evals/context_ab/results.md: score {s!r} must be between 0 and 1: {line}")
    return errors


def check(root: Path) -> list[str]:
    index = yaml.safe_load((root / "context" / "index.yaml").read_text(encoding="utf-8")) or {}
    documents = {c["id"] for c in index.get("concepts", []) if c.get("status") == "canonical"}
    return check_questions(root, documents) + check_results(root)


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked the context A/B design: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
