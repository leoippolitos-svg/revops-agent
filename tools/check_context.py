"""Check that the context documents and the catalog agree with each other.

Run from the repository root:
    python tools/check_context.py

It checks four things and exits with code 1 if any fails:

  1. Context documents: every document in context/index.yaml exists, its front
     matter id matches the index and the file name, and its status is valid.
     Each one follows the template: the required front matter, the five
     sections, a definition of at most three sentences, and no SQL.
  2. Annotations: every [[silver.model.column]], [[gold.model]] or
     [[concept:id]] in a document points at something that exists. Renaming a
     column without updating the documents fails here (docs/standards/
     context-documents.md).
  3. Catalog: every dbt model has a description, every column has a description,
     and every model file has an entry in a schema.yml (and the other way
     round). An undocumented model fails (docs/standards/data-modeling.md).
  4. Other documents: the company, area, metrics, CRM map, report and rule
     documents listed under "documents" in context/index.yaml. Each kind has its
     own required sections, all of them open with "Purpose", and their
     annotations are checked the same way. Only the kinds that hold a model
     query (crm-map, data-map) may contain a code block.
"""

import re
import sys
from pathlib import Path

import yaml

VALID_STATUS = {"draft", "canonical", "deprecated"}
REQUIRED_FRONT_MATTER = ("id", "title", "owner_team", "status", "last_reviewed", "related")
REQUIRED_SECTIONS = ("Definition", "Rules", "Gotchas", "Team differences", "Examples")
MAX_DEFINITION_SENTENCES = 3
# "planned" is only for index entries that have no document yet.
INDEX_STATUS = VALID_STATUS | {"planned"}
LAYERS = ("silver", "gold")
ANNOTATION = re.compile(r"\[\[([^\]]+)\]\]")
DOCUMENT_FRONT_MATTER = REQUIRED_FRONT_MATTER + ("kind",)
# Every kind of document has its own shape. "Purpose" comes first in all of them:
# what the document is for, who reads it and when, what does not belong in it,
# and who owns it. A new reader decides in one paragraph whether to keep reading.
KIND_SECTIONS = {
    "company": ("Purpose", "What Fernway sells", "Customers and segments", "How Fernway sells",
                "Systems and sources of truth", "Glossary"),
    "okrs": ("Purpose", "Cycle", "Objectives and key results", "Area, OKR and metric", "How the agent uses them"),
    "entities": ("Purpose", "Teams", "People and roles", "Segments", "Pipelines", "Resolving vague references"),
    "area": ("Purpose", "Mission", "People", "Objectives", "KPIs", "CRM objects", "Benchmarks",
             "Frequent questions", "Anti-confusions"),
    "metrics": ("Purpose", "Metrics", "Window and grain", "Internal benchmark", "Interpretation notes"),
    "crm-map": ("Purpose", "Pipelines and stages", "Fields", "Owners", "Loss reasons", "Where it lands in gold",
                "Model query", "Gotchas"),
    "data-map": ("Purpose", "Layers and access", "Tables and grain", "Canonical joins", "Model query",
                 "Validation queries", "Gotchas"),
    "report": ("Purpose", "Numbers and how they are computed", "Filters", "Gotchas", "Changelog"),
    "benchmark": ("Purpose", "How the agent uses them", "Benchmarks", "Sources"),
    "rule": ("Purpose", "Rules", "Owner and approvers"),
    "inventory": ("Purpose", "Items", "Rules for the agent"),
    "process": ("Purpose", "Steps", "Template"),
}
CODE_KINDS = {"crm-map", "data-map"}


def load_catalog(root: Path, errors: list[str]) -> dict[str, dict[str, str]]:
    """Return {"gold.mrr_monthly": {column: description, ...}, ...} from the dbt schema files."""
    catalog = {}
    models_dir = root / "pipeline" / "dbt" / "models"
    for layer in LAYERS:
        layer_dir = models_dir / layer
        if not layer_dir.is_dir():
            continue
        described = set()
        for schema in layer_dir.glob("schema.yml"):
            data = yaml.safe_load(schema.read_text(encoding="utf-8")) or {}
            for model in data.get("models", []):
                name = f"{layer}.{model['name']}"
                described.add(model["name"])
                where = schema.relative_to(root).as_posix()
                if not (model.get("description") or "").strip():
                    errors.append(f"{where}: model {model['name']} has no description")
                columns = {}
                for column in model.get("columns", []):
                    columns[column["name"]] = (column.get("description") or "").strip()
                    if not columns[column["name"]]:
                        errors.append(f"{where}: column {model['name']}.{column['name']} has no description")
                catalog[name] = columns
        files = {p.stem for p in layer_dir.glob("*.sql")}
        for missing in sorted(files - described):
            errors.append(f"{layer}/{missing}.sql has no entry in {layer}/schema.yml")
        for missing in sorted(described - files):
            errors.append(f"{layer}/schema.yml describes {missing}, which has no .sql file")
    return catalog


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    _, front, body = text.split("---", 2)
    return yaml.safe_load(front) or {}, body


def sections(body: str) -> dict[str, str]:
    """Split a document body into {"Definition": text, ...} by its "## " headings."""
    found, current = {}, None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            found[current] = ""
        elif current is not None:
            found[current] += line + "\n"
    return found


def structure_errors(where: str, front: dict, body: str) -> list[str]:
    """Check one document against the template (docs/standards/context-documents.md)."""
    errors = []
    for key in REQUIRED_FRONT_MATTER:
        if key not in front:
            errors.append(f"{where}: front matter is missing {key}")
    found = sections(body)
    for name in REQUIRED_SECTIONS:
        if name not in found:
            errors.append(f"{where}: missing the section '{name}'")
        elif not found[name].strip():
            errors.append(f"{where}: the section '{name}' is empty")
    # A sentence ends at . ! or ? followed by a space. Dots inside an annotation
    # such as [[silver.deal.stage]] are followed by a letter, so they do not count.
    definition = " ".join(found.get("Definition", "").split())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", definition) if s]
    if len(sentences) > MAX_DEFINITION_SENTENCES:
        errors.append(f"{where}: the definition has {len(sentences)} sentences, the maximum is "
                      f"{MAX_DEFINITION_SENTENCES}; if it needs more it is two concepts")
    if "```" in body:
        errors.append(f"{where}: context documents describe meaning, not implementation; remove the code block")
    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    catalog = load_catalog(root, errors)

    index_path = root / "context" / "index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    entries = {c["id"]: c for c in index.get("concepts", [])}
    for concept_id, entry in entries.items():
        if entry.get("status") not in INDEX_STATUS:
            errors.append(f"context/index.yaml: {concept_id} has invalid status {entry.get('status')!r}")

    documents = {cid for cid, e in entries.items() if e.get("status") != "planned"}
    other = {d["id"]: d for d in index.get("documents", [])}
    for clash in sorted(set(other) & set(entries)):
        errors.append(f"context/index.yaml: {clash} is listed both as a concept and as a document")
    for concept_id in sorted(documents):
        path = root / "context" / entries[concept_id]["path"]
        where = path.relative_to(root).as_posix()
        if not path.is_file():
            errors.append(f"{where}: listed in index.yaml but the file does not exist")
            continue
        front, body = split_front_matter(path.read_text(encoding="utf-8"))
        if front.get("id") != concept_id or path.stem != concept_id:
            errors.append(f"{where}: front matter id, file name and index id must all be {concept_id}")
        errors.extend(structure_errors(where, front, body))
        if front.get("status") not in VALID_STATUS:
            errors.append(f"{where}: status must be one of {sorted(VALID_STATUS)}")
        if front.get("status") != entries[concept_id].get("status"):
            errors.append(f"{where}: status differs between the document and context/index.yaml")
        for related in front.get("related", []):
            if related not in entries and related not in other:
                errors.append(f"{where}: related concept {related} is not in index.yaml")

        errors.extend(annotation_errors(path, where, catalog, documents, set(other)))

    errors.extend(document_errors(root, other, entries, catalog, documents))
    return errors


def document_errors(root: Path, other: dict, entries: dict, catalog: dict, concepts: set[str]) -> list[str]:
    """Check the non-concept documents: index entry, front matter, the sections of their kind."""
    errors = []
    for doc_id, entry in sorted(other.items()):
        kind = entry.get("kind")
        if kind not in KIND_SECTIONS:
            errors.append(f"context/index.yaml: {doc_id} has unknown kind {kind!r}; "
                          f"use one of {sorted(KIND_SECTIONS)}")
            continue
        if entry.get("status") not in VALID_STATUS:
            errors.append(f"context/index.yaml: {doc_id} has invalid status {entry.get('status')!r}")
        path = root / "context" / entry["path"]
        where = path.relative_to(root).as_posix()
        if not path.is_file():
            errors.append(f"{where}: listed in index.yaml but the file does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        front, body = split_front_matter(text)
        for key in DOCUMENT_FRONT_MATTER:
            if key not in front:
                errors.append(f"{where}: front matter is missing {key}")
        if front.get("id") != doc_id or path.stem != doc_id:
            errors.append(f"{where}: front matter id, file name and index id must all be {doc_id}")
        if front.get("kind") != kind:
            errors.append(f"{where}: kind differs between the document and context/index.yaml")
        if front.get("status") != entry.get("status"):
            errors.append(f"{where}: status differs between the document and context/index.yaml")
        found = sections(body)
        for name in KIND_SECTIONS[kind]:
            if name not in found:
                errors.append(f"{where}: a {kind} document needs the section '{name}'")
            elif not found[name].strip():
                errors.append(f"{where}: the section '{name}' is empty")
        if "```" in body and kind not in CODE_KINDS:
            errors.append(f"{where}: only {sorted(CODE_KINDS)} documents may hold a code block")
        for related in front.get("related", []):
            if related not in entries and related not in other:
                errors.append(f"{where}: related document {related} is not in index.yaml")
        errors.extend(annotation_errors(path, where, catalog, concepts, set(other)))
    return errors


def annotation_errors(path: Path, where: str, catalog: dict, concepts: set[str], docs: set[str]) -> list[str]:
    errors = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for ref in ANNOTATION.findall(line):
            if not annotation_exists(ref, catalog, concepts, docs):
                errors.append(f"{where}:{number}: annotation [[{ref}]] does not resolve")
    return errors


def annotation_exists(ref: str, catalog: dict, documents: set[str], docs: set[str] = frozenset()) -> bool:
    if ref.startswith("concept:"):
        return ref.removeprefix("concept:") in documents
    if ref.startswith("doc:"):
        return ref.removeprefix("doc:") in docs
    parts = ref.split(".")
    table = ".".join(parts[:2])
    if table not in catalog:
        return False
    return len(parts) == 2 or (len(parts) == 3 and parts[2] in catalog[table])


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked context documents and catalog: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
