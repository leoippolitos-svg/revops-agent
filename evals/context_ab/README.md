# Context A/B

The point of the context layer is that the same question gets a better answer with it than without it. This folder is the design of that comparison: the questions, what a correct answer must contain, and where the results go.

## Method

1. **Two arms, same everything else.** Same model, same gold data, same question. Arm A (`without_context`) gets the catalog only: table and column names and descriptions. Arm B (`with_context`) also gets the context documents through `search_context`.
2. **Questions are traps.** Each question in `questions.yaml` has a plausible wrong answer that a reader gets when they guess a definition (`trap`), and a short list of facts a correct answer must state (`must_include`).
3. **Scoring is a checklist, not a feeling.** An answer scores 1 point per `must_include` item it states and 0 for any item it contradicts. The score of an arm is the sum over all questions divided by the total number of items. Scoring is done by a person or by a judge model with the checklist; the judge never sees which arm produced the answer.
4. **Results are written down** in `results.md` with the date, the model, the commit and the number of questions. A run that was not made has the status `not run`, and no number.

## Files

| File | Contents |
|---|---|
| `questions.yaml` | The questions, their traps and their checklists |
| `results.md` | One table per run. Starts as `not run` |

## Rules

- Every question names the context document it depends on (`context_doc`), and that document must exist. `tools/check_context_ab.py` checks this.
- A checklist item comes from the document, not from taste. If the document does not say it, the item does not belong here.
- Never change a question after seeing a result to make an arm look better. Change it only when the document it depends on changes, and say so in the PR record.
- Questions that need a number from the data are not in this set. This set tests definitions and rules, which do not move when the data refreshes.

## Status

Design and questions only. No run has been made.
