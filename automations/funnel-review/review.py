"""Weekly funnel review, the evidence part. Spec: automations/funnel-review/SPEC.md.

Run from the repository root:
    python automations/funnel-review/review.py            # dry run: print the report
    python automations/funnel-review/review.py --write    # also write observability/logs/funnel-review-<data date>.md

This script is the deterministic half (ADR-0009): it compares mature cohorts, finds the stage
that moved most and lays out the evidence. It never states a cause. Reading the evidence and
naming a likely cause, with a confidence, is the agent's job with the funnel-diagnosis skill, so
the report ends with a hand-off section instead of a guess. It reads four gold tables read-only.
"""

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
# Qualification to negotiation, then the win. Each is (stage entered, column with deals that entered it,
# column with the deals it is divided by). deals_qualified is the cohort size, from funnel-stages.
STEPS = [
    ("discovery", "reached_discovery", "deals_qualified"),
    ("proposal", "reached_proposal", "reached_discovery"),
    ("negotiation", "reached_negotiation", "reached_proposal"),
    ("closed_won", "closed_won", "reached_negotiation"),
]
OPEN_STAGES = ["qualification", "discovery", "proposal", "negotiation"]
# Assumption, not a documented rule: who to ask about each stage. Qualification is handed over by an SDR.
OWNER_TEAM = {"qualification": "sdr", "discovery": "sales", "proposal": "sales", "negotiation": "sales", "closed_won": "sales"}
# Assumptions, not in funnel-stages.md: what counts as moving beyond normal. A smaller change is reported
# in the tables and does not name a constraint.
MIN_DROP_POINTS = 5.0
MIN_TIME_GROWTH = 0.5
MIN_TIME_DAYS = 3.0
MAX_DATA_AGE_DAYS = 7  # the review is weekly, so data older than a week is stale
PERIOD = 3  # the latest three mature cohorts and the three before them
TABLES = ("funnel_stage_monthly", "funnel_conversion_monthly", "funnel_time_in_stage_monthly", "data_quality_snapshot")
AUDIT_ATTENTION = re.compile(r"\*\*Attention, higher than the last report:\*\* (.+?)\.")


class ReviewError(RuntimeError):
    """The review cannot be trusted, so it stops and writes nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    """Maturity and minimum sample, read from funnel-stages.md, never from this file."""
    flat = " ".join((context_dir / "concepts" / "funnel-stages.md").read_text(encoding="utf-8").split())
    maturity = re.search(r"mature once (\d+) days have passed since the end of its month", flat)
    sample = re.search(r"needs at least (\d+) qualified deals", flat)
    if not maturity or not sample:
        raise ReviewError("funnel-stages.md no longer states the maturity or the minimum sample in the expected words")
    return {"maturity_days": int(maturity.group(1)), "min_deals": int(sample.group(1))}


def _rows(con, table: str) -> list[dict]:
    try:
        cursor = con.execute(f"SELECT * FROM gold.{table}")
    except duckdb.Error as error:
        raise ReviewError(f"cannot read gold.{table}: {error}") from error
    names = [c[0] for c in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def read_gold(db_path: Path) -> dict:
    if not db_path.is_file():
        raise ReviewError(f"lakehouse not found at {db_path}; build it with python tools/setup.py")
    con = duckdb.connect(str(db_path), read_only=True)  # the connection itself cannot write
    try:
        data = {table: _rows(con, table) for table in TABLES}
    finally:
        con.close()
    if len(data["data_quality_snapshot"]) != 1:
        raise ReviewError("gold.data_quality_snapshot should have one row")
    return data


def _month_end(first: date) -> date:
    return (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


def mature_cohorts(conversion: list[dict], as_of: date, maturity_days: int) -> list[dict]:
    """Cohorts old enough to have closed, oldest first. A newer cohort still looks worse than it is."""
    old = [r for r in conversion if _month_end(r["cohort_month"]) + timedelta(days=maturity_days) <= as_of]
    return sorted(old, key=lambda r: r["cohort_month"])


def _rate(rows: list[dict], top: str, bottom: str) -> float | None:
    denominator = sum(r[bottom] for r in rows)
    return sum(r[top] for r in rows) / denominator if denominator else None


def _weighted_median_days(time_rows: list[dict], stage: str, first: date, last: date) -> float | None:
    """Mean of the monthly medians, weighted by deals that left. A stand-in for a true median over all exits."""
    rows = [r for r in time_rows if r["stage"] == stage and first <= r["month"] <= last and r["median_days_in_stage"] is not None]
    weight = sum(r["deals_left"] for r in rows)
    return sum(r["median_days_in_stage"] * r["deals_left"] for r in rows) / weight if weight else None


def audit_flags(logs: Path, as_of: date, today: date) -> list[str]:
    """Flags the newest audit report of the same week raised, or [] when there is none or nothing rose."""
    for path in sorted(logs.glob("audit-*.md"), reverse=True):
        try:
            when = date.fromisoformat(path.stem.removeprefix("audit-"))
        except ValueError:
            continue
        if as_of - timedelta(days=MAX_DATA_AGE_DAYS) <= when <= today:
            match = AUDIT_ATTENTION.search(path.read_text(encoding="utf-8"))
            return match.group(1).split(", ") if match else []
    return []


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def build_report(data: dict, rules: dict, today: date, flags: list[str]) -> str:
    as_of = data["data_quality_snapshot"][0]["as_of"]
    if (today - as_of).days > MAX_DATA_AGE_DAYS:
        raise ReviewError(f"the data is from {as_of}, more than {MAX_DATA_AGE_DAYS} days old; refresh it first")
    cohorts = mature_cohorts(data["funnel_conversion_monthly"], as_of, rules["maturity_days"])
    lines = [f"# Weekly funnel review, data as of {as_of}", ""]
    if flags:
        lines += [f"**Data may explain a change:** the weekly audit raised {', '.join(flags)}. Rule this out before blaming the business.", ""]
    if len(cohorts) < 2 * PERIOD:
        return "\n".join(lines + [f"Only {len(cohorts)} mature cohorts exist and the review needs {2 * PERIOD}. No constraint is named.", ""])
    recent, previous = cohorts[-PERIOD:], cohorts[-2 * PERIOD:-PERIOD]
    names = {"recent": f"{recent[0]['cohort_month']:%Y-%m} to {recent[-1]['cohort_month']:%Y-%m}",
             "previous": f"{previous[0]['cohort_month']:%Y-%m} to {previous[-1]['cohort_month']:%Y-%m}"}
    sizes = {"recent": sum(r["deals_qualified"] for r in recent), "previous": sum(r["deals_qualified"] for r in previous)}
    lines += [f"Mature cohorts compared: recent {names['recent']} ({sizes['recent']} qualified deals), "
              f"previous {names['previous']} ({sizes['previous']}).", ""]
    if min(sizes.values()) < rules["min_deals"]:
        return "\n".join(lines + [f"A period has fewer than {rules['min_deals']} qualified deals, so the sample is too small. No constraint is named.", ""])

    lines += ["| Step | Previous | Recent | Change (points) | Extra deals lost |", "|---|---|---|---|---|"]
    scored = []
    for stage, top, bottom in STEPS:
        before, now = _rate(previous, top, bottom), _rate(recent, top, bottom)
        if before is None or now is None:
            lines.append(f"| into {stage} | n/a | n/a | n/a | n/a |")
            continue
        drop = (before - now) * 100
        lost = (before - now) * sum(r[bottom] for r in recent)  # deals lost compared with the previous rate
        lines.append(f"| into {stage} | {_pct(before)} | {_pct(now)} | {-drop:+.1f} | {lost:.1f} |")
        if drop >= MIN_DROP_POINTS:
            scored.append((lost, stage))
    lines += ["", "| Stage | Previous median days | Recent median days | Change |", "|---|---|---|---|"]
    time_rows, growth = data["funnel_time_in_stage_monthly"], []
    for stage in OPEN_STAGES:
        before = _weighted_median_days(time_rows, stage, previous[0]["cohort_month"], previous[-1]["cohort_month"])
        now = _weighted_median_days(time_rows, stage, recent[0]["cohort_month"], recent[-1]["cohort_month"])
        if before is None or now is None:
            lines.append(f"| {stage} | n/a | n/a | n/a |")
            continue
        lines.append(f"| {stage} | {before:.1f} | {now:.1f} | {now - before:+.1f} |")
        if before and now - before >= MIN_TIME_DAYS and (now - before) / before >= MIN_TIME_GROWTH:
            growth.append((now - before, stage))
    open_now, open_before = sum(r["still_open"] for r in recent), sum(r["still_open"] for r in previous)
    lines += ["", f"Still open in these cohorts: recent {open_now}, previous {open_before}. Time in stage only counts deals that "
                  "already left, so a good median can hide stuck deals. Compare it with these numbers.", ""]

    if scored:
        stage = max(scored)[1]
        lines.append(f"**Constraint: {stage}.** Conversion into {stage} fell the most, weighted by the deals that reached the step before it.")
    elif growth:
        stage = max(growth)[1]
        lines.append(f"**Constraint: {stage}.** No conversion fell by {MIN_DROP_POINTS:.0f} points, but time in {stage} grew the most.")
    else:
        return "\n".join(lines + ["No stage changed beyond its normal range.", ""])
    lines += [f"Owner team to ask: {OWNER_TEAM[stage]}.", "",
              "## Hand-off to the funnel-diagnosis skill", "",
              "- Likely cause: not stated here. This script never names a cause; the agent does, with a confidence level.",
              "- Rule out first: definition changes in `records/`, freshness, and the audit flags above.",
              f"- Check `search_records` for earlier work on {stage}.",
              "- Loss reason: unavailable. The CRM has none, so do not guess one.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly funnel review (dry run unless --write).")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb", help="DuckDB file")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs", help="where reports go and the audit is read")
    parser.add_argument("--date", default=date.today().isoformat(), help="today, to judge how old the data is")
    parser.add_argument("--write", action="store_true", help="write the report file")
    args = parser.parse_args(argv)

    try:
        today = date.fromisoformat(args.date)
        data = read_gold(args.db)
        as_of = data["data_quality_snapshot"][0]["as_of"]
        report = build_report(data, load_rules(), today, audit_flags(args.logs, as_of, today))
    except (ReviewError, ValueError, OSError) as error:
        # Never report a failure as "nothing changed": say it and stop.
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    print(report)
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"funnel-review-{as_of}.md"  # one file per data date, so a rerun overwrites it
        path.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {path}")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
