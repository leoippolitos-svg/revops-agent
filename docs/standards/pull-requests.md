# Pull requests

**Every unit of work ends in a pull request.** Code, analyses, automations, context changes and process changes all go through a PR. The PR is how the work gets reviewed, and the record it leaves is how the system remembers it was done.

## Work types

| Type | Example | The PR must include |
|---|---|---|
| `analysis` | Diagnosing a drop in SQL-to-opportunity conversion | Query, result, conclusion, record |
| `automation` | Lead routing rule | Spec, tests, record |
| `context` | New or corrected business rule | Updated context document, record |
| `process` | Change to the SDR → AE handoff | Process document, affected context docs, record |
| `data` | New gold model | Model, tests, catalog descriptions, context doc if a new concept, record |
| `app` | Micro-app | Full spec-driven flow (below), security checklist, record |
| `infra` | CI, tooling, connectors | Change, ADR if it is a decision, record |

## Flow

1. Branch from `main`: `<type>/<short-description>`, e.g. `context/mql-definition`.
2. Do the work. Update `context/` for every rule that changed.
3. Write the record with the `open-pr` skill.
4. Open the PR using the template.
5. Run the `pr-review` skill and address blockers.
6. CI green, then squash-merge. `main` is protected: no direct pushes, no force pushes.

## Spec-driven flow for `app` and `automation`

Research → Spec → Implement → QA → Security. The spec is written and committed before the code. Other work types do not need this ceremony.

## Records

Each PR adds one file to `records/` (template in `records/_template.md`). Records are indexed by the RAG, so the agent can answer "was this analyzed before, and what did we conclude?".

## Review

Reviews follow an evidence rule: every finding cites `file:line`, or an official URL for external claims. Findings without evidence are dropped.

| Severity | Meaning | Effect |
|---|---|---|
| Blocker | Wrong numbers, data leak, broken rule | Must fix before merge |
| Should-fix | Real defect, not a merge risk | Fix or justify |
| Nit | Style | Optional, max five |

For `context` and `analysis` PRs the review also checks that the definition used matches the canonical context document.

## The correction loop

When someone corrects an agent answer, the correction is not a chat message. It is a `context` PR. That is how the agent stops repeating the same mistake.
