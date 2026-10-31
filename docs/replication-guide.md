# Replicating this in a real company

How to stand up this RevOps agent in a real company: in what order, what is essential and what can wait, what goes wrong, and when it is ready for its first business user. It distils the build of the production system this repository recreates. Every path below is a file in this repository you can copy and fill.

## The idea in one sentence

**The agent is only as good as its context.** The code is small; the asset is the body of business rules, kept with discipline: pull requests, reviews and session closing. Start with the rules and the process, not the chat.

## Reference stack

| Need | This repository | In a company, also fine |
|---|---|---|
| Warehouse | DuckDB file, dbt bronze → silver → gold | Postgres, ClickHouse, BigQuery, Snowflake with dbt |
| CRM data | a generator of fictional exports | a mirror of the CRM in the warehouse, synced on a schedule |
| Context | Markdown in `context/`, checked in CI | the same; it is the part that matters |
| Agent | Python loop, Claude through a small adapter | the same, or the provider's SDK |
| Retrieval | BM25 in plain Python | add embeddings only when the eval says lexical is not enough |
| Scheduling | GitHub Actions | the same: versioned, with secrets and run logs |
| Chat for leaders | a local demo app | a hosted app with single sign-on and an allowlist |

## Order of construction

### Phase 0: process before code (1 to 2 days)
- Copy `CLAUDE.md`, `docs/standards/pull-requests.md`, `docs/standards/team-process.md` and the PR template. Protect `main`.
- Agree the session-closing rule (`context/rules/session-closing.md`) with the team: no task is finished until what it produced is in the repository.
- Set up the leak check and the secret scan before the first commit.

### Phase 1: the minimum context (1 to 2 weeks, then continuous)
Fill, in this order: `company`, `agent-security`, `routing.md`, `okrs`, `entities`, then **one area completely** (its area, metrics and CRM map documents) before touching a second one. A template left half-filled and loaded as required spends context on nothing and hides the real rule, so audit what each intent loads.

### Phase 2: the agent in the IDE (days)
The team uses the agent through their coding assistant first: it reads `AGENT.md` and the context, queries the warehouse read-only through an MCP or the tools. The human is in the loop the whole time; this is where the context gets corrected fastest.

### Phase 3: the CRM mirror (1 to 2 weeks)
Mirror the CRM into the warehouse instead of calling its API at question time: joins become SQL, there is no rate limit in the path of a question, and access control applies to commercial data. Mirror owners too, or "by person" questions have no answer. Track progress by checkpoint, not by sync time. Say when a base is truncated instead of computing a rate on it.

### Phase 4: retrieval (days)
Index the context by section, add the decisions and the project digests, and measure Hit@3 and MRR on real questions before trusting it. Reindex on every merge.

### Phase 5: the chat for leaders (2 to 3 weeks)
Single sign-on with the company domain checked on the server, an allowlist at the door, a database role per app, row-level security on conversations, and a visible notice that conversations are reviewed by the team. Build it from `apps/_template/` under `docs/standards/apps.md`.

### Phase 6: router, profiles and cost
Add the classification cascade, the profiles with fixed documents per intent, the four prompt blocks with cache, and the cost log (`agent/directives/routing.md`, ADR-0018). Cost per answer must be visible before usage grows.

### Phase 7: evaluation and smoke
An end-to-end eval that asserts the intent, the documents loaded, the tools offered and that answers carry no SQL or ids, on real questions; a smoke test of the authenticated path in production.

### Phase 8: writes, only with a clear pain
Every write is a deterministic automation with an authorization in `context/rules/writeback-rules.md`, a kill switch, a cap, a breaker, a read-back and a review queue. Sensitive fields go through proposals approved item by item.

## Essential versus later

| Essential: without it, it does not work or is not safe | Later |
|---|---|
| Context with company, security, routing, entities and one complete area | documents for every area |
| The session-closing rule | an automatic memory job |
| A read-only agent; writes only through automations | autonomous write-back |
| SQL guards in code and an allowlist of schemas | guards on query cost |
| Today's date in the prompt; rules over knowledge over tool results | few-shot examples in the prompt |
| Maps of owners and stages | a full org chart |
| An allowlist, company sign-in, row-level security, a role per app | filtering content by role (avoid it) |
| Reindexing on merge | a summary per chunk |
| A retrieval eval on real questions | a model as judge |
| Cost logged per answer | a cost dashboard |
| Secret scan and authorisation tests in CI | an AI security review (advisory) |
| A decision record for every closed decision | a long master document |

The files that ship with this repository are already sorted this way: the context documents marked essential in the list above, then the rest as the operation needs them.

## Pitfalls that cost real time

- **Data and answers.** The model guesses the date without it in the prompt. The same question gives three numbers until the definition is fixed in a document. The agent spends its whole budget discovering a schema until the CRM map names the table and shows one working query.
- **Infrastructure.** A shared database went down under one job's bulk load. A deploy status belonged to the previous deploy. Build-time and runtime variables were swapped.
- **Security.** A view inherited write grants. A grant copied from an old migration re-opened a closed table. An infrastructure tool echoed secrets into a transcript.
- **Process.** Rules lived where the team did not read them. A rule turned into a blocking check was rejected by the team. A vague "someone should configure X" was never done.

More in [lessons-learned.md](lessons-learned.md).

## Ready for the first business user

- [ ] An allowlist with the RevOps team; company sign-in checked on the server
- [ ] A route without a session gives 401; someone else's conversation gives 404 (automated tests)
- [ ] No tool that writes is exposed; the SQL guards are tested (several statements, comments, table functions, limits)
- [ ] Today's date, the hierarchy and "do not narrate" are in the prompt; answers carry no SQL or ids
- [ ] The owner and stage maps work
- [ ] The retrieval eval is above its target; reindexing on merge works
- [ ] Cost per answer is logged
- [ ] Three ready conversations answer real questions from leadership
- [ ] The end-to-end eval passes on the intents covered
- [ ] A visible notice says conversations are reviewed by the team
- [ ] The home penetration test passes (`docs/standards/security.md`)
