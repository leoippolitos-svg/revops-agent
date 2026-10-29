---
name: context-docs
description: Reads and writes context documents, the business definitions behind every metric and rule. Use when starting any task that touches data, metrics, business rules or agent answers, and when the user says "define this metric", "business rule", "context doc", "what counts as", or corrects an agent answer.
---

# Context documents

The full standard is in `docs/standards/context-documents.md`. This skill is the workflow.

## Reading (every task)

1. Open `context/index.yaml`.
2. Find every concept the task touches (metrics, funnel stages, customer status).
3. Read those documents before writing SQL or answering. Use the canonical definition, never a guess.
4. If a concept the task needs has no document, stop and say so. Creating it becomes part of the task.

## Writing or updating

1. Check `context/index.yaml` for an existing document. Update it instead of creating a near-duplicate.
2. Copy `context/_template.md` to `context/concepts/<id>.md`. The id is kebab-case and matches the filename.
3. Write the definition in at most three sentences, for an analyst in their first week.
4. Add rules, gotchas and team differences. Annotate every table and column you mention: `[[gold.table]]`, `[[gold.table.column]]`, `[[concept:other-id]]`.
5. Link to other concepts instead of repeating their rules.
6. Add or update the entry in `context/index.yaml`.
7. Set `last_reviewed` to today.

## Check before finishing

- One concept per document.
- No table or column descriptions (those go in dbt `schema.yml`).
- No SQL or implementation details.
- Every annotation points to something that exists.

## Example

User: "The agent counted trial accounts as customers."
Actions: open `active-customer.md`, add trials to the exclusion rules with an annotation to the plan-type column, add a worked example, update `last_reviewed`, open a `context` PR.
Result: the next answer excludes trials and cites the definition.

## Troubleshooting

- **Two documents define the same thing differently**: do not pick one silently. Mark the conflict under "Team differences" and ask the owner which is canonical.
- **Annotation check fails**: the model or column was renamed. Update the annotation, not the catalog.
