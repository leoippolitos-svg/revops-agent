"""Lexical retrieval over the context documents (ADR-0007, ADR-0012).

The one interface the agent uses is `retrieve(question, k)`. A vector backend can replace
this file later without touching the agent.

    python agent/rag/retrieve.py "Are trial accounts counted as customers?"

The index is built in memory from the files on every call, so nobody can ever query a
half-built index (docs/standards/rag.md). Only the standard library is used.
"""

import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Common words carry no meaning for ranking and would match every document.
STOPWORDS = frozenset(
    "a an and are as at be by can do does for from has have how if in is it its of on or "
    "that the their there this to was we what when where which who why will with you our "
    "should would".split()
)
# Standard BM25 constants: k1 limits how much repeating a word helps, b adjusts for length.
K1, B = 1.5, 0.75
# A heading repeated in the chunk text counts more than the same word in the body.
HEADING_WEIGHT = 2


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    status: str
    title: str
    section: str
    text: str


def tokenize(text: str) -> list[str]:
    """Lowercase words, with a light suffix strip so 'deals' matches 'deal'."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [_stem(w) for w in words if w not in STOPWORDS]


def _stem(word: str) -> str:
    for suffix in ("ies", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def split_document(text: str) -> tuple[dict, list[tuple[str, str]]]:
    """Return the front matter and the (section heading, body) pairs of a document."""
    _, front, body = text.replace("\r\n", "\n").split("---\n", 2)
    sections, heading, lines = [], "", []
    for line in body.splitlines():
        if line.startswith("## "):
            if lines:
                sections.append((heading, "\n".join(lines).strip()))
            heading, lines = line[3:].strip(), []
        elif not line.startswith("# "):
            lines.append(line)
    if lines:
        sections.append((heading, "\n".join(lines).strip()))
    return yaml.safe_load(front) or {}, [(h, t) for h, t in sections if t]


def load_chunks(context_dir: Path) -> list[Chunk]:
    """One chunk per section of every document listed in the index. Planned entries have no file."""
    index = yaml.safe_load((context_dir / "index.yaml").read_text(encoding="utf-8"))
    chunks = []
    for entry in index.get("concepts", []):
        path = context_dir / entry["path"]
        if entry["status"] == "planned" or not path.is_file():
            continue
        front, sections = split_document(path.read_text(encoding="utf-8"))
        for heading, body in sections:
            chunks.append(Chunk(entry["id"], entry["status"], front.get("title", entry["id"]), heading, body))
    return chunks


def chunk_tokens(chunk: Chunk) -> list[str]:
    # The title and the heading go in with extra weight: they say what the section is about.
    head = f"{chunk.title} {chunk.section}"
    return tokenize(" ".join([head] * HEADING_WEIGHT + [chunk.text]))


def rank(question: str, chunks: list[Chunk]) -> list[tuple[float, Chunk]]:
    """All chunks with a positive BM25 score, best first. Ties keep the corpus order."""
    docs = [chunk_tokens(c) for c in chunks]
    average = sum(len(d) for d in docs) / len(docs) if docs else 0
    scored = []
    for chunk, tokens in zip(chunks, docs):
        score = 0.0
        for word in set(tokenize(question)):
            frequency = tokens.count(word)
            if not frequency:
                continue
            containing = sum(1 for d in docs if word in d)
            idf = math.log(1 + (len(docs) - containing + 0.5) / (containing + 0.5))
            score += idf * frequency * (K1 + 1) / (frequency + K1 * (1 - B + B * len(tokens) / average))
        if score > 0:
            scored.append((score, chunk))
    return sorted(scored, key=lambda pair: -pair[0])


def retrieve(question: str, k: int = 3, context_dir: Path | None = None) -> list[dict]:
    """The k best context sections, each with its document id and status."""
    if k < 1:
        raise ValueError("k must be at least 1")
    context_dir = context_dir or Path(__file__).resolve().parents[2] / "context"
    return [
        {"doc_id": c.doc_id, "status": c.status, "section": c.section, "text": c.text, "score": round(s, 3)}
        for s, c in rank(question, load_chunks(context_dir))[:k]
    ]


def ranked_documents(question: str, context_dir: Path | None = None) -> list[str]:
    """Document ids in order of their best section, each once. Used by the evals."""
    context_dir = context_dir or Path(__file__).resolve().parents[2] / "context"
    seen: list[str] = []
    for _, chunk in rank(question, load_chunks(context_dir)):
        if chunk.doc_id not in seen:
            seen.append(chunk.doc_id)
    return seen


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/rag/retrieve.py "question"', file=sys.stderr)
        return 1
    for hit in retrieve(argv[1]):
        print(f"{hit['score']:6.2f}  {hit['doc_id']} ({hit['status']}) / {hit['section']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
