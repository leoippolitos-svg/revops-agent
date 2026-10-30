---
name: run-evals
description: Runs and records the evaluation sets for retrieval, routing and skill triggers, and explains any metric that moves. Use when the user asks to "run the evals", "measure retrieval", "check router accuracy", "test the skills", or when a change touches context documents, routing, tools or a skill description.
---

# Run the evals

Targets are in `docs/standards/rag.md`: Hit@3 at least 0.90, MRR at least 0.75, router accuracy at least 0.90.

## Steps

1. Validate the case files first: `python tools/check_evals.py` and `python tools/check_skills.py`. A broken case file would score zero for the wrong reason.
2. Run what exists. Say plainly which sets have no scoring code yet; an unmeasured set is "not measured", never a number.
3. Record each metric with the date, the commit and the number of cases.
4. Compare with the last recorded value. If a metric dropped, find which cases changed rank and why.
5. Put the table in the PR record. A PR that lowers a metric must explain it.
6. Never edit a case to make it pass. Fix the document, the chunk or the routing rule. A case changes only when the expected answer is truly wrong, and the record says so.
7. Live runs that call a model need the owner's key in their own shell. Do not read `.env`.

## Example

Retrieval: Hit@3 0.93, MRR 0.78 over 40 cases, down from 0.95 and 0.81. Three cases moved after a context document was split. The record names them and the change.

## Troubleshooting

- **All cases fail**: check the index loaded before suspecting the cases.
- **A skill triggers on a should_not case**: tighten its description, not the case.

## Never

- Report a metric that was not computed.
- Change targets to match results.
