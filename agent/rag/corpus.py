"""What retrieval can search, by category, and how a file becomes chunks.

    python agent/rag/corpus.py          # count files and chunks per category

Five categories, after the reference design's memory taxonomy:

| Category    | Holds                                              | Why it is searched                     |
|-------------|----------------------------------------------------|----------------------------------------|
| domain      | the concept documents (definitions)                | what the business means; the default search |
| reference   | the other context documents: company, areas, metrics, maps, reports, rules | read whole as fixed documents of an intent; searchable on request |
| decisions   | ADRs and memory/decisions                          | what was decided, so it is not reopened |
| conventions | docs/standards                                     | how work is done here                   |
| incidents   | project digests (projects/*/CONTEXT.md)            | what was tried, what failed, what is open |

Records stay in their own tool (search_records). A file is split by its "## " headings, and a
long section by paragraph, never in the middle of a heading. A project digest shorter than
MIN_DIGEST_CHARS is an empty template and is skipped.
"""

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MAX_CHUNK_CHARS = 2_000
MIN_DIGEST_CHARS = 600
CATEGORIES = ("domain", "reference", "decisions", "conventions", "incidents")


@dataclass(frozen=True)
class Source:
    doc_id: str
    category: str
    status: str
    path: Path


def file_hash(path: Path) -> str:
    """SHA-256 of the file with line endings normalised, so a Windows checkout and a Linux runner agree."""
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def sources(root: Path = ROOT) -> list[Source]:
    found = []
    index = yaml.safe_load((root / "context" / "index.yaml").read_text(encoding="utf-8")) or {}
    # Concepts are the default search. The other documents are long and overlap the concepts
    # they link to; mixed into the default search they pushed the definitions out of the top 3
    # (Hit@3 0.88, MRR 0.68 when tried), so an intent loads them whole by id instead.
    for key, category in (("concepts", "domain"), ("documents", "reference")):
        for entry in index.get(key, []):
            path = root / "context" / entry["path"]
            if entry.get("status") != "planned" and path.is_file():
                if not path.resolve().is_relative_to((root / "context").resolve()):
                    raise ValueError(f"index entry '{entry['id']}' points outside the context folder")
                found.append(Source(entry["id"], category, entry["status"], path))
    for folder in ("docs/adr", "memory/decisions"):
        for path in sorted((root / folder).glob("*.md")):
            if path.name not in ("README.md", "_template.md"):
                found.append(Source(path.stem, "decisions", "canonical", path))
    for path in sorted((root / "docs" / "standards").glob("*.md")):
        found.append(Source(f"standard-{path.stem}", "conventions", "canonical", path))
    for path in sorted((root / "projects").glob("*/CONTEXT.md")):
        if path.parent.name != "_template" and len(path.read_text(encoding="utf-8")) >= MIN_DIGEST_CHARS:
            found.append(Source(f"project-{path.parent.name}", "incidents", "canonical", path))
    return found


def chunks_of(text: str) -> list[tuple[str, str, str]]:
    """(title, section heading, text) pieces of one file, split by "## " and then by paragraph."""
    text = text.replace("\r\n", "\n")
    if text.startswith("---\n"):
        front_text, text = text[4:].split("\n---\n", 1)
        front = yaml.safe_load(front_text) or {}
    else:
        front = {}
    title = front.get("title") or next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    pieces, heading, lines = [], "", []

    def flush():
        body = "\n".join(lines).strip()
        if not body:
            return
        # A long section is cut at paragraph boundaries so no chunk swallows a whole document.
        current = ""
        for paragraph in body.split("\n\n"):
            if current and len(current) + len(paragraph) > MAX_CHUNK_CHARS:
                pieces.append((title, heading, current.strip()))
                current = ""
            current += paragraph + "\n\n"
        if current.strip():
            pieces.append((title, heading, current.strip()))

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            heading, lines = line[3:].strip(), []
        elif not line.startswith("# "):
            lines.append(line)
    flush()
    return pieces


def main() -> int:
    counts = {c: [0, 0] for c in CATEGORIES}
    for source in sources():
        counts[source.category][0] += 1
        counts[source.category][1] += len(chunks_of(source.path.read_text(encoding="utf-8")))
    for category, (files, chunks) in counts.items():
        print(f"{category:12} {files:4} files {chunks:5} chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
