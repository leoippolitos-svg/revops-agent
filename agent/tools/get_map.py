"""get_map: deterministic lookup of a closed map, so names and orders are never guessed.

    python agent/tools/get_map.py owners

The model chooses a key from MAPS and nothing else. A key is never turned into a path or a
query, so the tool cannot read anything that is not listed here (ADR-0019). Two kinds of map:

- a fixed SELECT over gold, through query_gold, for facts that live in data (who is who,
  the order of the stages);
- one section of a context document, looked up by id in the index, for facts that live in
  documents (the teams and what they own, the segments, the apps).

Retrieval is probabilistic; this is not. "Dana's deals" needs the owner id behind the name,
and an answer that may not show ids needs the name behind every id.
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

from query_gold import query_gold  # noqa: E402

# key: (description for the model, kind, source)
MAPS = {
    "owners": ("Owner id, full name and team of every person who owns deals or companies.",
               "query", "SELECT owner_id, full_name, team FROM gold.owner_directory ORDER BY owner_id"),
    "funnel_stages": ("Every funnel stage value with its order, from qualification to the closed stages.",
                      "query", "SELECT DISTINCT stage, stage_order FROM gold.funnel_stage_monthly ORDER BY stage_order, stage"),
    "teams": ("The teams, the value stored for each, what they own and whether they receive leads.",
              "section", ("entities", "Teams")),
    "segments": ("The company segments and how they are defined.", "section", ("entities", "Segments")),
    "pipelines": ("The CRM pipelines and what is not tracked as a pipeline.", "section", ("entities", "Pipelines")),
    "apps": ("The internal apps and what each one computes.", "section", ("apps", "Items")),
}


class UnknownMap(ValueError):
    """The key is not one of MAPS."""


def _section(doc_id: str, heading: str, root: Path) -> str:
    index = yaml.safe_load((root / "context" / "index.yaml").read_text(encoding="utf-8")) or {}
    entry = next(e for e in index.get("concepts", []) + index.get("documents", []) if e["id"] == doc_id)
    text = (root / "context" / entry["path"]).read_text(encoding="utf-8")
    body = text.split(f"\n## {heading}\n", 1)[1]
    return body.split("\n## ", 1)[0].strip()


def get_map(key: str, root: Path = ROOT, db_path: Path | None = None) -> dict:
    if key not in MAPS:
        raise UnknownMap(f"Unknown map {key!r}. Known maps: {', '.join(MAPS)}.")
    description, kind, source = MAPS[key]
    if kind == "query":
        result = query_gold(source, db_path=db_path)
        return {"key": key, "description": description, "columns": result["columns"], "rows": result["rows"]}
    doc_id, heading = source
    return {"key": key, "description": description, "document": doc_id, "text": _section(doc_id, heading, root)}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: python agent/tools/get_map.py <{'|'.join(MAPS)}>", file=sys.stderr)
        return 1
    try:
        print(json.dumps(get_map(argv[1]), indent=2, default=str))
    except UnknownMap as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
