# Apps

How a micro-app is created, where it lives and what it must pass before anyone uses it. The skill `new-micro-app` follows this standard; the security rules are in [security.md](security.md).

## Why a standard

In the reference design, one internal app was down for a day because of three failures of "a pattern that did not exist yet": a missing grant, a credential shared between apps and a build variable set as a runtime one. After that, every app was born from one template with one stack, and the playbook below ran before the first deploy.

## Where apps live

- One folder per app: `apps/<app-name>/`, with `SPEC.md`, `README.md`, the code, and its tests in `tests/test_<app_name>.py`.
- Every app has a row in the `apps` context document, which says what it computes so the agent can explain its numbers. `tools/check_apps.py` fails when a folder has no row or no README.
- An app with its own history across sessions also gets a project folder in `projects/`, listed in `WORKSPACE.md`.

## The stack

One stack, not a choice per app:

- Python, reading gold only through `query_gold`, the same guard as the agent and the MCP server.
- Output is a static HTML page built from fixed queries: no form, no script, no server to attack, styled with `design-system/tokens.json`.
- An app that needs people to sign in or to write data is a different class of app. It needs a decision record first, and then the engineering rules 1 to 17 apply in full (single sign-on, allowlist, one credential per app, row-level security).

## Creating an app: the playbook

| Step | What | Output |
|---|---|---|
| 0 | Diagnose: who uses it, which decision it supports, which gold tables, what already exists. Five lines, no invented paths. | a note in the spec's Problem section |
| 1 | Copy `apps/_template/` to `apps/<app-name>/` and fill `SPEC.md`. Commit the spec before any code. | the spec |
| 2 | Build the smallest version that answers the spec, from `app.py` in the template. | the code |
| 3 | Tests: the main path, an empty result, stale data, escaping of every value, and that the page holds no form or script. | `tests/test_<app_name>.py` |
| 4 | Hardening: tick the micro-app checklist in the security standard; register any connection in `connectors/registry.yaml`; add the row to the `apps` context document and a report document if it shows numbers. | ticked checklist |
| 5 | Report every checklist item as passed or failed in the pull request, with what is left for a person. | the PR description |

## Mistakes that already cost production elsewhere

- A build-time variable and a runtime secret swapped places: the app built and then could not reach its database.
- A grant copied from an old migration re-opened a table that had been closed on purpose.
- A status page said "deployed" for the previous deploy; wait for the new deploy id before saying it is live.
