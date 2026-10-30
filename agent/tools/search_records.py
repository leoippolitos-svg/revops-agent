"""search_records: "was this analyzed before, and what did we conclude?" (ADR-0006).

    python agent/tools/search_records.py "what did we conclude about time in stage"

A thin wrapper over agent/rag/record_search.py with the same input rules as search_context.
It returns the title, the date and the conclusion of each record, and nothing else from it.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent" / "rag"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_search import search_records as find_records  # noqa: E402
from search_context import InvalidInput, check_search_input  # noqa: E402


def search_records(question: str, k: int = 3, records_dir: Path | None = None) -> dict:
    """The k best past records for a question, each with title, date and conclusion."""
    check_search_input(question, k)
    return {"results": (results := find_records(question, k, records_dir)), "count": len(results)}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/tools/search_records.py "question"', file=sys.stderr)
        return 1
    try:
        print(json.dumps(search_records(argv[1]), indent=2))
    except InvalidInput as error:
        print(f"InvalidInput: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
