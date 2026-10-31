# Security

## Principles

1. **The agent advises, it does not execute.** It reads gold and answers. It never writes to a data source, sends messages or changes records on its own.
2. **Rules are enforced outside the model.** A rule written only in a prompt is a wish. Read-only database connections, denied commands and CI checks are what actually hold.
3. **Least privilege.** Every connector gets the smallest scope that works, recorded in `connectors/registry.yaml`.

## Rule zero: nothing real gets in

Three layers, none of which depend on the model remembering:

| Layer | Catches | How |
|---|---|---|
| Pre-commit hook | Real company terms, before the commit exists | `tools/hooks/pre-commit` runs `tools/check_leaks.py` |
| CI `rule-zero` job | The same, on every PR and push | `LEAK_TERMS` GitHub secret |
| CI `secrets` job | Keys and tokens | gitleaks |

The list of forbidden terms is never committed: locally it lives in `.leak-terms` (gitignored), in CI in the `LEAK_TERMS` secret. The check prints only `file:line`, never the term.

## Secrets

- Secrets live only in `.env`, which is gitignored. `.env.example` lists the names with empty values.
- The coding agent is denied access to `.env` in `.claude/settings.json`.
- CI runs gitleaks on every PR.

## Data

- All data is synthetic. Even fictional data contains no realistic personal identifiers (no real-looking tax IDs or phone numbers).
- The MCP server opens DuckDB in read-only mode and exposes the `gold` schema only.

## Micro-app checklist

Every app in `apps/` passes this before merge:

- [ ] No secret in client code or in the repository
- [ ] Reads data only through gold, read-only
- [ ] All inputs validated on the server side
- [ ] No raw SQL built from user input; parameters only
- [ ] Errors logged without leaking internal details to the user
- [ ] Dependencies pinned
- [ ] Spec and security review committed with the PR

## Automation checklist

- [ ] Idempotent: running twice does not duplicate effects
- [ ] Retries with backoff, and a cap
- [ ] Respects rate limits of every API it calls
- [ ] Failures are logged and alerted, never swallowed
- [ ] Credentials scoped to the minimum and registered
- [ ] Dry-run mode for anything that would write to an external system
- [ ] A kill switch (`<NAME>_ENABLED`) that turns writes off without a deploy, and a cap per run from `context/rules/writeback-rules.md`
- [ ] A circuit breaker on consecutive failures, a check after every write, and "needs review" (never "skipped") for anything not written
- [ ] Matches on an explicit id only, never on a name, and no silent back-fill past a date cutoff
- [ ] A `RECURRING-AUTHORIZATION` for the automation in the write-back rules (`tools/check_automations.py` enforces it)

## Engineering rules for any code that serves people or data

Twenty rules, each born from a real failure in the reference design. They apply to every app, job and tool here, and to any code an AI writes in this repository. Where the current code has no such surface yet (no login, no database writes), the rule waits for the first code that has it.

1. **Authorisation is checked on the server.** A hidden button is not access control; every route and action checks the session itself.
2. **Sessions live in HttpOnly, Secure, SameSite cookies**, never in browser storage.
3. **Every new table ships with its row-level security and its grants in the same migration.** A table without them is readable by anyone with the public key.
4. **The admin credential is used only by jobs and scripts**, from one module, never by an app.
5. **Every input is validated at the entry**: request bodies, query strings, files and external API responses.
6. **No IDOR**: a query with an id from the client also filters by the user or tenant, and someone else's record returns 404, not 403.
7. **Writes happen only in protected server routes or actions**, never from the client straight to the database.
8. **One data-access layer is the only door to the database.** CI fails if code outside it opens a connection. Here, that door is `query_gold`.
9. **No SSRF**: server-side requests go only to hosts on an allowlist.
10. **An internal app is single sign-on plus a domain check on the server plus an allowlist table.** Access is decided at the door, not by filtering content per role.
11. **A write across several tables runs in one transaction**; concurrency is handled by constraints, not by hoping.
12. **In production, the full error goes to the server log and a generic message to the user.**
13. **Integrity lives in the database**: foreign keys, not-null, unique and check constraints cover the invariants.
14. **AI runs on the server, with no personal identifiers in prompts**, and logs carry no personal data.
15. **Deploy environment variables live only in the deploy panel**, and infrastructure tools never auto-approve a write.
16. **A new app runs the app playbook before its first deploy** ([docs/standards/apps.md](apps.md)).
17. **Each app has its own database credential** with the least grants it needs; never a shared superuser.
18. **A new micro-app starts from the template** in `apps/_template/`.
19. **Before calling an infrastructure tool, check whether it can echo secrets.** Some return environment variables in plain text; when in doubt, treat it as if it does.
20. **Never log the whole error object in code that builds a connection from a URL**: the error carries the full connection string. Log the message only.

### Engineering practices that go with them

- Authorisation tests ship with the feature: no session gives 401, another user's record gives 404.
- Dependencies are pinned and audited; a critical or high finding blocks the merge.
- The secret scan runs on every pull request with no path filter, because keys hide in Markdown and at the root.
- Security headers on every response; CORS never `*` on an authenticated API.
- Rate limits on login, notifications and any paid API (model calls included).
- A health endpoint with no external dependency.
- Never read `.env` with a shell command: check that a variable exists with a boolean, and if a value ever leaks, say so at once without repeating it and rotate it.

### If a request breaks a rule

Say which rule it breaks and propose the safe alternative. Never build it "just to test". This applies to people and to AI alike.

### Security review before every merge

Report each item as passed, failed or not applicable; a failed critical item blocks the merge. Green checks are not this review: an AI review job once passed on the pull request and reported its finding only after the merge.

- Secrets: none hard-coded, none in client code, `.env.example` only has names, the secret scan passed.
- Data: new tables have row-level security and grants in the same migration; grants were compared with the live database, never copied from an old migration.
- Routes: every route checks the session; ids from the client are filtered by owner; inputs validated; rate limits where needed; outbound hosts on the allowlist.
- Output: no raw HTML from user content; errors generic to the user.
- AI and logs: no personal data in prompts or logs.
- Dependencies: audited; authorisation tests pass.

### Home penetration test before real data

| Step | Expected |
|---|---|
| Open an internal URL in a private window | redirected to login, no data visible even for a moment |
| Call every API route without a cookie | 401 or 403, never 200 with data |
| Call the database API with the public key on each table | empty list or permission error |
| Signed in as A, change an id to one of B's records | 404 |
| Search the built bundle for secret names | nothing but public values |
| Re-read the transcript of every infrastructure tool call | no secret echoed |

### When a secret leaks

Rotate first, investigate second: revoke the value at its provider, set the new one in the deploy panel or CI secrets, redeploy, then find how it leaked and add the check that would have caught it.
