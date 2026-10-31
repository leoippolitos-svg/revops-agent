"""Incremental index of the retrieval corpus, by file hash.

    python agent/rag/ingest.py            # update data/rag-index.json, only files that changed
    python agent/rag/ingest.py --force    # rebuild every file
    python agent/rag/ingest.py --check    # exit 1 if the index is out of date

The agent's lexical search reads the files directly, so it never needs this index. The index
exists for the step that does cost something: embeddings, if vectors are ever added
(ADR-0007). It keeps, per file, the SHA-256 of its text with line endings normalised and its
chunks, so a reingest re-chunks (and would re-embed) only what changed, removes files that
left the corpus, and never reprocesses everything because a Windows checkout and a Linux
runner disagree on line endings. The file is written whole at the end, so a failed run
leaves the previous index as it was.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus import ROOT, chunks_of, file_hash, sources  # noqa: E402

INDEX = ROOT / "data" / "rag-index.json"


def ingest(root: Path = ROOT, index_path: Path = INDEX, force: bool = False) -> dict:
    old = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() and not force else {"files": {}}
    files, report = {}, {"added": [], "changed": [], "unchanged": [], "removed": []}
    for source in sources(root):
        rel = source.path.relative_to(root).as_posix()
        digest = file_hash(source.path)
        previous = old["files"].get(rel)
        if previous and previous["sha256"] == digest:
            files[rel] = previous
            report["unchanged"].append(rel)
            continue
        files[rel] = {"doc_id": source.doc_id, "category": source.category, "status": source.status, "sha256": digest,
                      "chunks": [{"title": t, "heading": h, "text": x} for t, h, x in chunks_of(source.path.read_text(encoding="utf-8"))]}
        report["changed" if previous else "added"].append(rel)
    report["removed"] = sorted(set(old["files"]) - set(files))
    index_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temporary file and swap it in: nobody ever reads a half-written index.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=index_path.parent, delete=False) as handle:
        json.dump({"files": files}, handle)
    os.replace(handle.name, index_path)
    return report


def is_current(root: Path = ROOT, index_path: Path = INDEX) -> bool:
    if not index_path.is_file():
        return False
    files = json.loads(index_path.read_text(encoding="utf-8"))["files"]
    current = {s.path.relative_to(root).as_posix(): file_hash(s.path) for s in sources(root)}
    return current == {rel: f["sha256"] for rel, f in files.items()}


def main(argv: list[str]) -> int:
    if "--check" in argv:
        ok = is_current()
        print("the retrieval index is up to date" if ok else "the retrieval index is out of date: run python agent/rag/ingest.py")
        return 0 if ok else 1
    report = ingest(force="--force" in argv)
    print(", ".join(f"{len(v)} {k}" for k, v in report.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
