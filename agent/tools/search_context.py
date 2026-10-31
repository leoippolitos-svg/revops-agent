"""search_context: the agent's tool for business definitions (ADR-0006, ADR-0012).

    python agent/tools/search_context.py "Are trial accounts counted as customers?"

A thin wrapper over agent/rag/retrieve.py. It checks the input, because the input comes
from a language model, and adds a warning when a section is not from a canonical document.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent" / "rag"))

from corpus import CATEGORIES  # noqa: E402
from retrieve import retrieve  # noqa: E402

MAX_QUESTION_CHARS = 500
MAX_K = 5

# Said next to a section so the answer can tell the reader how far to trust it.
WARNINGS = {
    "draft": "This document is a draft and may change. Say so in the answer.",
    "deprecated": "This document is deprecated. Do not use it as the current definition.",
}


class InvalidInput(ValueError):
    """The question or k was refused before any search."""


def check_search_input(question, k) -> None:
    """The input rules shared by the two search tools. Raises InvalidInput."""
    if not isinstance(question, str) or not question.strip():
        raise InvalidInput("The question must be a non-empty string.")
    if len(question) > MAX_QUESTION_CHARS:
        raise InvalidInput(f"The question is longer than {MAX_QUESTION_CHARS} characters.")
    # bool is an int in Python, so True would otherwise pass as k=1.
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= MAX_K:
        raise InvalidInput(f"k must be a whole number from 1 to {MAX_K}.")


def search_context(question: str, k: int = 3, context_dir: Path | None = None, category: str = "domain") -> dict:
    """The k best sections for a question, each with its document id, status and category.

    `category` is one of corpus.CATEGORIES: domain (definitions, the default), reference
    (company, areas, metrics, maps, rules), decisions, conventions or incidents (project history)."""
    check_search_input(question, k)
    if category not in CATEGORIES:
        raise InvalidInput(f"category must be one of {', '.join(CATEGORIES)}.")
    results = retrieve(question, k, context_dir, categories=(category,))
    for result in results:
        if result["status"] in WARNINGS:
            result["warning"] = WARNINGS[result["status"]]
    return {"results": results, "count": len(results)}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/tools/search_context.py "question"', file=sys.stderr)
        return 1
    try:
        print(json.dumps(search_context(argv[1]), indent=2))
    except InvalidInput as error:
        print(f"InvalidInput: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
