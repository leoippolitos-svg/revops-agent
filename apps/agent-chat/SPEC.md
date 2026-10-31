# Agent chat, Spec

Status: built

## Problem
The agent runs only from the command line, so nobody can see how it works without reading code. Leaders in the reference design used a web chat; this app is the local, no-key version of that chat. It shows every answer together with how it was produced: the route, the documents loaded, the prompt blocks, the tools offered and called. It exists to demonstrate and document the agent, not to serve a team.

## Users
- Whoever evaluates the project (a reviewer, an interviewer) running it on their own machine.
- RevOps, to see the route and the context a question gets before a model is ever called.

## Screens
One page.

1. **Thread**: each question with its answer. In demo mode the answer starts with "Demo answer: no language model was called".
2. **How the agent got here**, under each answer: intent and the cascade step that chose it, model tier and budget, tools offered, documents always loaded, skill, the four prompt blocks with their size and cache flag, tools called, model calls, and the mode.
3. **Ask box** and four example questions, one of them a write request that the agent refuses.

## Data read
Gold tables only, through the agent's read-only tools:

- `gold.mql_monthly`
- `gold.mrr_monthly`
- `gold.active_customer_monthly`
- `gold.funnel_conversion_monthly`
- `gold.owner_workload`
- `gold.data_quality_snapshot`

Plus the context documents and records, through `search_context` and `search_records`.

## Must never
- Write to any data source, or offer a tool that can write
- Listen on anything but 127.0.0.1
- Accept a request from another web page (Origin check) or anything but one JSON field
- Run a third-party script in the page, or put data into the page as HTML
- Call a model unless started with `--model` and a key in the environment
- Log the question text

## Security checklist
Standard: `docs/standards/security.md`, micro-app checklist. This app is a local server with a page that runs a script, a different class from the static apps; ADR-0023 records the decision.

- [x] No secret in client code or in the repository. The key, when used, is read from the environment on the server only.
- [x] Reads data only through gold, read-only. Every query goes through `query_gold`; tested.
- [x] All inputs validated on the server side. One JSON field, at most 500 characters, at most 4 KB body; tested.
- [x] No raw SQL built from user input; parameters only. The demo model picks from fixed queries; with a model, `query_gold` parses and refuses anything but one read.
- [x] Errors logged without leaking internal details to the user. The page gets a generic message, the console gets the detail; tested.
- [x] Dependencies pinned. None added: standard library only.
- [x] Spec and security review committed with the PR.
