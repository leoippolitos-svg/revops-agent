"""App name: one read-only page. Copy this folder to apps/<app-name>/ and rename this file.

    python apps/<app-name>/app.py --out page.html

Spec: apps/<app-name>/SPEC.md. Standard: docs/standards/apps.md.
The page is static HTML built from fixed queries, so it has no inputs, no script and no
server to attack. Every query goes through query_gold, the one door to the data.
"""

import argparse
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

from query_gold import QueryFailed, QueryRejected, default_db_path, query_gold  # noqa: E402

# Fixed text with no parameters: nothing a visitor sends can ever reach a query.
QUERIES = {
    "example": "SELECT month, ending_mrr_usd FROM gold.mrr_monthly ORDER BY month",
}
EMPTY = "no data for this period"  # never a zero: a missing month is not a month with nothing


def render(db_path: Path) -> str:
    """Build the whole page. Every value is escaped, because data can hold any text."""
    rows = query_gold(QUERIES["example"], db_path=db_path)["rows"]
    if not rows:
        body = f"<p>{EMPTY}</p>"
    else:
        cells = "".join(f"<tr><td>{html.escape(str(r['month'])[:7])}</td>"
                        f"<td>{html.escape(str(r['ending_mrr_usd']))}</td></tr>" for r in rows)
        body = f"<table><tr><th>Month</th><th>Ending MRR</th></tr>{cells}</table>"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>App name</title></head><body>{body}</body></html>"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the page.")
    parser.add_argument("--out", required=True, help="where to write the HTML file")
    parser.add_argument("--db", default=None, help="DuckDB file (defaults to the local lakehouse)")
    args = parser.parse_args(argv)
    try:
        page = render(Path(args.db) if args.db else default_db_path())
    except (QueryRejected, QueryFailed) as error:
        # Full detail on the console for whoever runs it; the page is never written half-built.
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    Path(args.out).write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
