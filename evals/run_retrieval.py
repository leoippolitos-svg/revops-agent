"""Score retrieval on evals/retrieval_cases.yaml: Hit@3 and MRR.

Run from the repository root:
    python evals/run_retrieval.py           # print the scores and the misses
    python evals/run_retrieval.py --check   # also exit 1 if a target is missed

Targets come from docs/standards/rag.md: Hit@3 >= 0.90 and MRR >= 0.75. A case is one
question with one expected document, and the rank is the position of that document in the
list of documents ordered by their best section.
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "rag"))

from retrieve import ranked_documents  # noqa: E402

TARGET_HIT_AT_3 = 0.90
TARGET_MRR = 0.75


def score(cases: list[dict], context_dir: Path) -> tuple[float, float, list[tuple[str, str, list[str]]]]:
    hits, reciprocal, misses = 0, 0.0, []
    for case in cases:
        ranking = ranked_documents(case["question"], context_dir)
        if case["expected"] in ranking:
            position = ranking.index(case["expected"]) + 1
            reciprocal += 1 / position
            hits += position <= 3
            if position > 3:
                misses.append((case["question"], case["expected"], ranking[:3]))
        else:
            misses.append((case["question"], case["expected"], ranking[:3]))
    return hits / len(cases), reciprocal / len(cases), misses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score retrieval (Hit@3 and MRR).")
    parser.add_argument("--check", action="store_true", help="exit 1 if a target is missed")
    args = parser.parse_args(argv)

    cases = yaml.safe_load((ROOT / "evals" / "retrieval_cases.yaml").read_text(encoding="utf-8"))["cases"]
    hit, mrr, misses = score(cases, ROOT / "context")
    for question, expected, got in misses:
        print(f"MISS expected {expected}, got {got}: {question}")
    print(f"\n{len(cases)} cases: Hit@3 {hit:.3f} (target {TARGET_HIT_AT_3}), MRR {mrr:.3f} (target {TARGET_MRR})")
    if args.check and (hit < TARGET_HIT_AT_3 or mrr < TARGET_MRR):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
