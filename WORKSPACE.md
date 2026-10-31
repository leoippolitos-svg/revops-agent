# Workspace

Where work lives in this repository, and the index of projects. Read it before starting anything that will take more than one pull request.

## Where things go

| Folder | Holds | Lifetime |
|---|---|---|
| `context/` | Stable rules: what the business means and how the data works | timeless, changed by pull request |
| `projects/<name>/` | One folder per line of work that spans sessions: `README.md` (what it is, where it runs, who owns it) and `CONTEXT.md` (the session history) | as long as the work lives |
| `analyses/<YYYY-MM-name>/` | One finished analysis: query, output, result | permanent |
| `records/` | One record per merged pull request | permanent, never edited after merge |
| `memory/` | Decisions the agent treats as final, patterns found, internal baselines | until revoked |
| `BACKLOG.md` | Pending items that must not get lost between sessions | items move to Done, never deleted |

A stable fact goes to `context/`; the story of how it was found goes to the project's `CONTEXT.md`. See the `session-closing` context document.

## Projects

| Project | Kind | Owner (role) | Where it runs | Status |
|---|---|---|---|---|
| [revops-agent](projects/revops-agent/README.md) | app | RevOps lead | locally, tests only | built, never run with a real model |
| [funnel-review](projects/funnel-review/README.md) | automation | RevOps lead | locally, not scheduled | built, assumptions waiting on the owner |

New project: copy `projects/_template/` to `projects/<short-name>/`, fill both files, and add a row here in the same pull request.
