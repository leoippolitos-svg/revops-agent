"""get_catalog: what a table and its columns are (ADR-0002, ADR-0006).

    python agent/tools/get_catalog.py gold.mrr_monthly

Reads the dbt schema.yml files, never the database, so it works without the lakehouse and
cannot leak a row. It reuses the loader behind docs/catalog.md so the two never disagree.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_catalog import LAYERS, documents_using, load_models  # noqa: E402


class UnknownModel(ValueError):
    """The name is not a model in the catalog. It is rejected, never looked up elsewhere."""


def _catalog(root: Path) -> dict[str, dict]:
    """Every model by its full name, "gold.mrr_monthly"."""
    return {f"{layer}.{m['name']}": m | {"layer": layer} for layer, _, _ in LAYERS for m in load_models(root, layer)}


def get_catalog(model: str, root: Path | None = None) -> dict:
    """The description of one model and its columns, and the context documents that use it."""
    root = root or ROOT
    catalog = _catalog(root)
    if not isinstance(model, str) or not model.strip():
        raise UnknownModel("Give a model name such as gold.mrr_monthly.")
    name = model.strip().lower()
    if "." not in name:
        # Gold comes first: it is the layer the agent reads, and no name exists in both.
        name = next((f"{layer}.{name}" for layer, _, _ in LAYERS if f"{layer}.{name}" in catalog), name)
    if name not in catalog:
        known = ", ".join(sorted(n for n in catalog if n.startswith("gold.")))
        raise UnknownModel(f"'{model.strip()[:60]}' is not in the catalog. Gold models: {known}.")

    entry = catalog[name]
    return {
        "model": name,
        "layer": entry["layer"],
        "description": " ".join(str(entry["description"]).split()),
        "columns": [{"name": c["name"], "description": " ".join(str(c["description"]).split())}
                    for c in entry["columns"]],
        "context_documents": [doc_id for doc_id, _ in documents_using(root).get(name, [])],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python agent/tools/get_catalog.py gold.mrr_monthly", file=sys.stderr)
        return 1
    try:
        print(json.dumps(get_catalog(argv[1]), indent=2))
    except UnknownModel as error:
        print(f"UnknownModel: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
