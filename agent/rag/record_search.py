"""Lexical search over the past records in records/ (ADR-0007, ADR-0012).

    python agent/rag/record_search.py "what did we conclude about time in stage"

Same BM25 ranking as the context documents (retrieve.py). Each record is one chunk, because
a record is short and its sections only make sense together.
"""

import sys
from pathlib import Path

from retrieve import Chunk, rank, split_document

CONCLUSION = "Result or decision"
# The folder README and the blank template are not records.
NOT_RECORDS = {"README.md", "_template.md"}


def load_records(records_dir: Path) -> list[tuple[Chunk, dict]]:
    """One (chunk, details) pair per record, in file name order, which is date order."""
    loaded = []
    for path in sorted(records_dir.glob("*.md")):
        if path.name in NOT_RECORDS:
            continue
        text = path.read_text(encoding="utf-8")
        front, sections = split_document(text)
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        by_name = dict(sections)
        chunk = Chunk(path.stem, str(front.get("type", "")), title, "", "\n".join(body for _, body in sections))
        loaded.append((chunk, {
            "record": path.stem,
            "title": title,
            "date": str(front.get("date", "")),
            "type": str(front.get("type", "")),
            "pr": str(front.get("pr", "")),
            "conclusion": by_name.get(CONCLUSION, ""),
        }))
    return loaded


def search_records(question: str, k: int = 3, records_dir: Path | None = None) -> list[dict]:
    """The k best matching records with their title, date and conclusion."""
    if k < 1:
        raise ValueError("k must be at least 1")
    records_dir = records_dir or Path(__file__).resolve().parents[2] / "records"
    loaded = load_records(records_dir)
    details = {chunk.doc_id: info for chunk, info in loaded}
    ranked = rank(question, [chunk for chunk, _ in loaded])
    return [{**details[chunk.doc_id], "score": round(score, 3)} for score, chunk in ranked[:k]]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/rag/record_search.py "question"', file=sys.stderr)
        return 1
    for hit in search_records(argv[1]):
        print(f"{hit['score']:6.2f}  {hit['date']}  {hit['record']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
