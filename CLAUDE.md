# CLAUDE.md

Instructions for the coding agent working in this repository. Keep this file short: it is an index, the details live in `docs/standards/`.

## Rule zero: everything is fictional

Never add real company data, customer names, numbers, prompts, table or field names from any employer or client. Use the fictional company **Fernway** (see `generator/README.md`). If something looks too specific to a real business, generalize it before writing it down. This is enforced by `tools/check_leaks.py` in the pre-commit hook and in CI.

## Scope

Work only inside this repository. Never read, write or run commands against folders outside it. Policy files (`.claude/settings.json`) are changed by the owner, outside an agent session.

## Before any task

1. Load the `context-docs` skill and read `context/index.yaml`.
2. Decide the work type: `analysis`, `automation`, `context`, `process`, `data`, `app` or `infra`.
3. Create a branch named `<type>/<short-description>`.

## Every task ends in a pull request

No exceptions, including analyses and context changes. A PR is ready when:

- the checks pass,
- a record exists in `records/` (use the `open-pr` skill),
- every business rule that changed is updated in `context/`,
- the session is closed: the project digest in `projects/<name>/CONTEXT.md` is written and every scratch file is promoted or deleted (context document `session-closing`; the project index is `WORKSPACE.md`),
- the PR template is filled in.

Rules: [docs/standards/pull-requests.md](docs/standards/pull-requests.md)

## Standards

| Topic | File |
|---|---|
| Context documents | [docs/standards/context-documents.md](docs/standards/context-documents.md) |
| Data modeling and naming | [docs/standards/data-modeling.md](docs/standards/data-modeling.md) |
| Skills | [docs/standards/skills.md](docs/standards/skills.md) |
| Pull requests | [docs/standards/pull-requests.md](docs/standards/pull-requests.md) |
| Security | [docs/standards/security.md](docs/standards/security.md) |
| Apps | [docs/standards/apps.md](docs/standards/apps.md) |
| Team process and git | [docs/standards/team-process.md](docs/standards/team-process.md) |
| Verification | [docs/standards/verification.md](docs/standards/verification.md) |
| Automations | [docs/standards/automations.md](docs/standards/automations.md) |
| Audits | [docs/standards/audits.md](docs/standards/audits.md) |
| Investigation | [docs/standards/investigation.md](docs/standards/investigation.md) |
| Continuous learning | [docs/standards/continuous-learning.md](docs/standards/continuous-learning.md) |
| Multi-agent work | [docs/standards/multi-agent.md](docs/standards/multi-agent.md) |
| Prompt patterns | [docs/standards/prompt-patterns.md](docs/standards/prompt-patterns.md) |
| Connectors | [docs/standards/connectors.md](docs/standards/connectors.md) |
| RAG | [docs/standards/rag.md](docs/standards/rag.md) |

## Writing code

- Everything in English: code, comments, docs, commit messages.
- The owner is learning Python. Comment the *why* wherever the logic is not obvious, in plain language.
- Prefer simple Python over frameworks. A new dependency or a new agent tool needs an ADR in `docs/adr/`.

## Never

- Commit secrets or read `.env`.
- Edit the bronze layer by hand. Bronze is written only by ingestion.
- Give the RevOps agent write access to any data source.
- Copy third-party skills or code into the repo, except unmodified, under a license that allows it, pinned to a version and listed in `THIRD_PARTY.md` (Anthropic's `skill-creator` is the first). Never edit such a copy in place.
