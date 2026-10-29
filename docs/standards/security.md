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
