"""Score the router: accuracy on router_cases.yaml and on router_heldout.yaml.

Run from the repository root:
    python evals/run_router.py           # print the accuracy of each file and the misses
    python evals/run_router.py --check   # also exit 1 if either file is under the target

The target is 0.90 (docs/standards/rag.md). The held-out file was written before the router
and never used to tune it, so it is the number to trust more.
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

from router import route  # noqa: E402

TARGET_ACCURACY = 0.90
FILES = ("router_cases.yaml", "router_heldout.yaml")


def score(cases: list[dict]) -> tuple[float, list[tuple[str, str, str]]]:
    misses = []
    for case in cases:
        got = route(case["question"])["intent"]
        if got != case["intent"]:
            misses.append((case["question"], case["intent"], got))
    return 1 - len(misses) / len(cases), misses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score the router.")
    parser.add_argument("--check", action="store_true", help="exit 1 if a file is under the target")
    args = parser.parse_args(argv)

    failed = False
    for name in FILES:
        cases = yaml.safe_load((ROOT / "evals" / name).read_text(encoding="utf-8"))["cases"]
        accuracy, misses = score(cases)
        for question, expected, got in misses:
            print(f"MISS expected {expected}, got {got}: {question}")
        print(f"{name}: {len(cases)} cases, accuracy {accuracy:.3f} (target {TARGET_ACCURACY})\n")
        failed |= accuracy < TARGET_ACCURACY
    return 1 if args.check and failed else 0


if __name__ == "__main__":
    sys.exit(main())
