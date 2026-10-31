"""Revenue snapshot: one read-only page with MRR, customers, funnel and MQLs.

    python apps/revenue-snapshot/snapshot.py --out snapshot.html

Spec: apps/revenue-snapshot/SPEC.md. It writes one static HTML file, so the page has no
inputs, no script and no server to attack. The four queries below are fixed text and go
through query_gold, the same guard the agent and the MCP server use, so the page can read
gold and nothing else. It has never been opened in a real browser or hosted anywhere.
"""

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

from query_gold import QueryFailed, QueryRejected, default_db_path, query_gold  # noqa: E402

STALE_DAYS = 2  # the spec: older than two days, the page says so at the top
TOKENS = json.loads((ROOT / "design-system" / "tokens.json").read_text(encoding="utf-8"))

# Fixed text, no parameters: nothing a visitor can send ever reaches a query.
QUERIES = {
    "mrr": "SELECT month, new_mrr_usd, churned_mrr_usd, ending_mrr_usd FROM gold.mrr_monthly ORDER BY month",
    "customers": "SELECT month, active_customers, active_subscriptions FROM gold.active_customer_monthly ORDER BY month",
    "funnel": "SELECT month, stage, stage_order, deals_entered FROM gold.funnel_stage_monthly ORDER BY month, stage_order",
    "mqls": "SELECT month, marketing_mqls, sales_mqls FROM gold.mql_monthly ORDER BY month",
}
# Block title and the context document that defines it.
BLOCKS = {"mrr": ("MRR", "mrr"), "customers": ("Customers", "active-customer"),
          "funnel": ("Funnel", "funnel-stages"), "mqls": ("MQLs", "mql")}
EMPTY = "no data for this period"  # never a zero: a missing month is not a month with nothing


def definition(doc_id: str, root: Path = ROOT) -> str:
    """The first sentence of the document's Definition section, so the page never words it twice."""
    text = (root / "context" / "concepts" / f"{doc_id}.md").read_text(encoding="utf-8")
    body = text.split("## Definition", 1)[1].split("##", 1)[0].strip()
    return re.split(r"(?<=\.)\s", body, maxsplit=1)[0]


def _month(value) -> str:
    return str(value)[:7]


def _money(value) -> str:
    return f"${value:,.0f}"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return f"<p class='empty'>{EMPTY}</p>"
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _blocks(data: dict[str, list[list]]) -> dict[str, str]:
    """Each block's body. The newest month is the one in progress, so it is labelled and kept out of the headline."""
    out = {}
    mrr = data["mrr"]
    if mrr:
        partial = _month(mrr[-1][0])
        rows = [[_month(m) + (" (partial)" if _month(m) == partial else ""), _money(n), _money(c), _money(e)]
                for m, n, c, e in mrr]
        full = mrr[-2] if len(mrr) > 1 else None
        note = (f"<p>Latest full month {_month(full[0])}: new {_money(full[1])}, churned {_money(full[2])}.</p>"
                if full else f"<p class='empty'>{EMPTY} (no full month yet)</p>")
        out["mrr"] = note + _table(["Month", "New MRR", "Churned MRR", "Ending MRR"], rows)
    else:
        out["mrr"] = _table([], [])
    partial = _month(data["customers"][-1][0]) if data["customers"] else None
    out["customers"] = _table(["Month", "Active customers", "Active subscriptions"],
                              [[_month(m) + (" (partial)" if _month(m) == partial else ""), c, s]
                               for m, c, s in data["customers"]])
    months = sorted({_month(r[0]) for r in data["funnel"]})
    if len(months) > 1:
        latest = months[-2]  # the newest month is partial, so the funnel shows the one before
        out["funnel"] = (f"<p>Deals that entered each stage in {latest}.</p>" +
                         _table(["Stage", "Deals entered"], [[s, d] for m, s, _, d in data["funnel"] if _month(m) == latest]))
    else:
        out["funnel"] = _table([], [])
    partial = _month(data["mqls"][-1][0]) if data["mqls"] else None
    # Marketing's count is shown. Sales' count only says whether it agrees, and the two are never added.
    out["mqls"] = _table(["Month", "Marketing MQLs", "Sales"],
                         [[_month(m) + (" (partial)" if _month(m) == partial else ""), mk,
                           "Sales agrees" if mk == sl else "Sales counts differently"] for m, mk, sl in data["mqls"]])
    return out


def _load(db_path: Path) -> dict[str, list[list]] | None:
    """The four result sets, or None when gold cannot be read. Details go to the log, never the page."""
    if not db_path.is_file():
        print("snapshot: the lakehouse file is missing", file=sys.stderr)
        return None
    try:
        return {name: query_gold(sql, db_path)["rows"] for name, sql in QUERIES.items()}
    except (QueryFailed, QueryRejected) as error:
        print(f"snapshot: {type(error).__name__}", file=sys.stderr)
        return None


def render(db_path: Path | None = None, now: float | None = None) -> str:
    db_path = db_path or default_db_path()
    data = _load(db_path)
    banners = []
    if data is None:
        banners.append("Gold is not available right now. No data is shown.")
        data = {name: [] for name in QUERIES}
    else:
        age_days = ((now or time.time()) - db_path.stat().st_mtime) / 86400
        if age_days > STALE_DAYS:
            banners.append(f"This data is {int(age_days)} days old. It was last refreshed more than {STALE_DAYS} days ago.")
    bodies = _blocks(data)
    newest = max((_month(r[0]) for rows in data.values() for r in rows), default=None)
    through = f"Data through {newest}. The newest month is still in progress, so it is partial." if newest else EMPTY

    color, size, space = TOKENS["color"], TOKENS["typography"]["size"], TOKENS["spacing"]
    css = (f"body{{margin:0;background:{color['background']};color:{color['text']};font-family:{TOKENS['typography']['family']};"
           f"font-size:{size['body']};line-height:{TOKENS['typography']['line-height']}}}"
           f"main{{max-width:760px;margin:0 auto;padding:{space['md']}}}"
           f"h1{{font-size:{size['title']}}}h2{{font-size:{size['heading']};color:{color['primary']}}}"
           f"section{{background:{color['surface']};border:1px solid {color['border']};border-radius:{TOKENS['radius']['card']};"
           f"padding:{space['md']};margin-bottom:{space['md']}}}"
           f"table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:{space['xs']} {space['sm']};"
           f"border-bottom:1px solid {color['border']}}}"
           f".definition,.empty{{color:{color['text-muted']};font-size:{size['small']}}}"
           f".banner{{background:#fff4e0;border:1px solid {color['accent']};padding:{space['sm']} {space['md']};"
           f"margin-bottom:{space['md']}}}"
           f"@media print{{body{{background:#fff}}section{{break-inside:avoid;margin-bottom:{space['sm']}}}}}")
    parts = [f"<div class='banner' role='alert'>{html.escape(b)}</div>" for b in banners]
    parts += [f"<p class='definition'>{html.escape(through)}</p>"]
    for key, (title, doc_id) in BLOCKS.items():
        parts.append(f"<section><h2>{title}</h2>{bodies[key]}<p class='definition'>{html.escape(definition(doc_id))} "
                     f"<a href='../../context/concepts/{doc_id}.md'>Definition: {doc_id}</a></p></section>")
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'><title>Revenue snapshot</title>"
            f"<style>{css}</style></head><body><main><h1>Revenue snapshot</h1>{''.join(parts)}</main></body></html>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the revenue snapshot page.")
    parser.add_argument("--out", required=True, help="where to write the HTML file")
    args = parser.parse_args(argv)
    Path(args.out).write_text(render(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
