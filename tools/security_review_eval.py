"""Decide the outcome of an AI security review: red on HIGH or CRITICAL, and say it where people look.

    python tools/security_review_eval.py claudecode-results.json [--notify] [--summary summary.md]

The review action writes its findings as JSON. This script turns them into a decision the
pull request cannot miss: exit code 1 (a red check) when any finding is HIGH or CRITICAL,
a short summary for the job page, and, with --notify, one Slack alert through the shared
notifier (simulated unless its kill switch and webhook are set). MEDIUM and LOW findings are
listed but do not fail the check: the review comments on them in the pull request.

It reads only the findings file; it never sees a secret, and it does not print the code.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKING = {"HIGH", "CRITICAL"}


def load_findings(path: Path) -> list[dict]:
    """Accept {"findings": [...]} or a bare list; an unreadable file is itself a failure, never a pass."""
    if not path.is_file():
        raise ValueError(f"no findings file at {path}: the review did not run, which is not a pass")
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = data.get("findings", []) if isinstance(data, dict) else data
    if not isinstance(findings, list):
        raise ValueError("the findings file has no list of findings")
    return [f for f in findings if isinstance(f, dict)]


def decide(findings: list[dict]) -> tuple[bool, str]:
    blocking = [f for f in findings if str(f.get("severity", "")).upper() in BLOCKING]
    lines = ["## AI security review", "",
             f"{len(findings)} finding(s), {len(blocking)} blocking (HIGH or CRITICAL).", ""]
    for f in sorted(findings, key=lambda f: str(f.get("severity", "")).upper() not in BLOCKING):
        lines.append(f"- **{str(f.get('severity', '?')).upper()}** `{f.get('file', '?')}:{f.get('line', '?')}`: "
                     f"{str(f.get('description', '')).strip()[:200]}")
    if not findings:
        lines.append("No finding. Green is not a full review: authorisation and grant changes are still read by hand.")
    return bool(blocking), "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turn AI security review findings into a decision.")
    parser.add_argument("findings", type=Path)
    parser.add_argument("--summary", type=Path, help="write the summary here (for the job page)")
    parser.add_argument("--notify", action="store_true", help="send one Slack alert when something blocks")
    args = parser.parse_args(argv)
    try:
        findings = load_findings(args.findings)
    except (ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    blocked, summary = decide(findings)
    print(summary)
    if args.summary:
        args.summary.write_text(summary, encoding="utf-8")
    if blocked and args.notify:
        sys.path.insert(0, str(ROOT / "observability"))
        from notify import send
        top = [f"{str(f.get('severity')).upper()} {f.get('file')}:{f.get('line')}" for f in findings
               if str(f.get("severity", "")).upper() in BLOCKING][:5]
        send("security-review", "The AI security review found a blocking issue", top, write=True)
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
