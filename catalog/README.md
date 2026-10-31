# Run catalog

One card per thing that runs: automations, scheduled jobs, the agent, apps and servers. The table of all cards is generated in [docs/run-catalog.md](../docs/run-catalog.md).

## Fields

| Field | Meaning |
|---|---|
| `id` | the file name, kebab-case |
| `name`, `purpose` | what it is and why it exists |
| `kind` | automation, agent, app, job or server |
| `owner` | the role that answers for it |
| `trigger` | what starts it: a schedule, an event, a person |
| `where` | the spec or the code, as a path in this repository |
| `writes` | what it changes anywhere, or "nothing" |
| `ai`, `cost` | the model it calls, if any, and what it costs |
| `status_source` | where its health comes from: `github_actions` (a workflow), `log` (a file pattern in the log folder) or `none`; `expected_every_days` makes a late run visible |
| `rerun_ok` | optional; `true` only for a job that reads or syncs idempotently, so the on-call agent and the watchdog may start it again |
| `situation` | `active` (runs on its own), `manual` (runs when a person runs it) or `stopped` (kept for history, never deleted) |

## Rules

- Creating, changing or stopping something that runs is not finished until its card is (context document `session-closing`).
- A workflow that runs on a schedule must have a card; `python tools/catalog.py check` fails otherwise.
- An active item needs a status source, or nobody sees it break.
