---
date: 2026-10-30
type: data
pr: "#21"
author: Leonardo Ippolito
---

# Context A/B: design, questions and an honest results file

## What was done
Added `evals/context_ab/` with the method (`README.md`), 14 question cases (`questions.yaml`) and a results file (`results.md`) that starts as `not run`. Added `tools/check_context_ab.py` with 4 tests, wired into the pre-commit hook, CI `standards`, `make check` and `tools/setup.py`.

## Why
The claim of the context layer is that the same question gets a better answer with it. The repo should show how that claim would be tested, so it is not left as an assertion.

## Result or decision
- Two arms differ only in context: the catalog alone, against the catalog plus the context documents.
- Each question is a trap with a plausible wrong answer and a checklist taken from a context document. All five canonical documents are covered.
- Scoring is a checklist, and the judge does not see which arm produced the answer.
- Questions test definitions and rules, not numbers, so they do not change when data refreshes.
- The checker fails if a question depends on a missing document, if a canonical document has no question, or if `results.md` shows a score on a row marked `not run` or a score outside 0 to 1.
- No run has been made. There is no with-context or without-context score, and none is claimed.

## Rules and context changed
none

## Follow-ups
Run the comparison once the agent and the `search_context` tool exist, and add the first row to `results.md`. Phase 6: an example micro-app.
