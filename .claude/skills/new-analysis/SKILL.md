---
name: new-analysis
description: Runs a business analysis as code, with the query, the result and the definitions used, and ships it as an analysis PR. Use when the user asks to "analyze", "investigate", "find out why", "look into" a metric or a drop, or wants a number that needs more than one query.
---

# New analysis

Standard: `docs/standards/pull-requests.md`. An analysis that is not in the repo cannot be found, reviewed or repeated.

## Steps

1. Write the question in one sentence and the decision it supports. If there is no decision, ask for one.
2. Load `context-docs`. Read every concept the question touches and the `cross-cutting-rules` document. If a concept has no canonical document, stop and say so.
3. Search `records/` for earlier work on the same topic. Quote its conclusion, and say whether this analysis confirms or changes it.
4. Create `analyses/YYYY-MM-<short-description>/` and branch `analysis/<short-description>`.
5. Write `query.sql`. Read from the `gold` schema only, with the lakehouse opened read-only. Use the absolute path in `LAKEHOUSE_PATH`, because a relative path resolves from the current folder.
6. Run it and keep the output next to the query. Note the data date, which is the newest export loaded.
7. Pick the business skill that fits the question from the map in `agent/skills/README.md` (cohorts, forecast, risk, statistical check) and follow it. For a number that does not match, follow `docs/standards/investigation.md`: hypotheses written before querying, a list of ids as proof.
8. Rule out data causes before business causes: freshness, the flags in `cross-cutting-rules`, a changed definition. Say what you checked.
9. Write `result.md`: the conclusion in the first line, then the evidence, the definitions used (with their context documents), the tables read and the caveats.
10. If the analysis shows a rule is wrong or missing, update `context/` in the same PR.
11. Open the PR with `open-pr`, type `analysis`.

## `result.md` shape

Use these headings, in this order: the conclusion as the title, `Data as of`, `Evidence`, `Definitions used`, `Tables read`, `Caveats`, `What would change this conclusion`.

## Example

Question: "Did entries into proposal fall in September?" Conclusion: "Entries into proposal fell 18% against August; the drop starts in qualification, not in proposal." The folder holds the query, the output, and a note that September is a full month, so the comparison is fair.

## Troubleshooting

- **The number does not match a dashboard**: compare definitions first, then the data date. Do not adjust your query to match.
- **The month in progress is in the range**: it is partial. Exclude it or label it.
- **A needed column is not in gold**: that is a `data` task. Open it separately instead of reading silver.

## Never

- Query bronze or silver to answer a business question.
- Report a conclusion without the definition it used.
