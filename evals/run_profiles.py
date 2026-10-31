"""Score the profile eval: right intent, right documents loaded, right tools offered.

    python evals/run_profiles.py [--check]

What it covers: the plan the agent makes before calling a model (route, fixed documents,
tools), for every case in evals/profile_cases.yaml. A case accepts a set of intents,
because demanding one tests the toss of the classifier rather than the agent.
What it does not cover: the answer. No model is called, so prose, numbers and tone are
untested; a green run is not "answers checked".
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

import agent  # noqa: E402

TARGET = 1.0  # deterministic: every case must pass


def score(cases: list[dict]) -> tuple[float, list[str]]:
    failures = []
    for case in cases:
        decision = agent.route(case["question"])
        prompt = agent.build_system_prompt(decision)
        problems = []
        if decision["intent"] not in case["intents"]:
            problems.append(f"intent {decision['intent']} not in {case['intents']}")
        problems += [f"document {d} not loaded" for d in case["must_load"] if f"Document `{d}`" not in prompt]
        problems += [f"tool {t} not offered" for t in case["must_offer"] if t not in decision["tools"]]
        if problems:
            failures.append(f"{case['question']!r}: " + "; ".join(problems))
    return 1 - len(failures) / max(len(cases), 1), failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score the profile eval.")
    parser.add_argument("--check", action="store_true", help="exit 1 if a case fails")
    args = parser.parse_args(argv)
    cases = yaml.safe_load((ROOT / "evals" / "profile_cases.yaml").read_text(encoding="utf-8"))["cases"]
    rate, failures = score(cases)
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"profile_cases.yaml: {len(cases)} cases, pass rate {rate:.3f} (target {TARGET})")
    return 1 if args.check and rate < TARGET else 0


if __name__ == "__main__":
    sys.exit(main())
