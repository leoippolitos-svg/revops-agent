# Environment setup

How to set up a machine and a repository so that AI agents work well here from the first session: what loads by itself, which skills and checks exist, how MCP servers get their credentials without a secret ever sitting in a config file.

## The pieces

| Piece | Role | Here |
|---|---|---|
| Rules loaded in every session | what an agent must know before touching anything | `CLAUDE.md`, which links the standards |
| The agent's manual | identity, reading order, rules for answers | `agent/directives/AGENT.md` |
| Context | the business rules | `context/` |
| Skills | repeatable procedures | `.claude/skills/` (coding agent), `agent/skills/` (RevOps agent) |
| Reviewer agents | an independent check before "done" | `.claude/agents/` |
| MCP servers | tools the agent can call | `mcp_server/` and others, configured from `mcp.template.json` |
| Permissions and hooks | what an agent may never do | `.claude/settings.json`, owned by the repository owner |
| Checks | what CI refuses | `tools/`, `.github/workflows/ci.yml` |

## Step by step

1. **Machine.** Python 3.12, Git, the GitHub CLI, the coding assistant. Clone, create a virtual environment, `pip install -r requirements.txt`, `python tools/setup.py`.
2. **Rules always loaded.** `CLAUDE.md` stays short and links the standards; long rules live in their own file. A short copy of a long rule declares its source and is checked by `tools/check_derived.py`.
3. **Process skills first.** Before business skills: `context-docs`, `open-pr`, `pr-review`, `session-closing`, `refinement`, and Anthropic's `skill-creator` for building more.
4. **MCP servers and credentials.** Copy the block you need from `mcp.template.json` into your client's configuration. Values are `${env:NAME}` placeholders, never literal secrets. When a client cannot resolve environment variables, start the server through `tools/mcp_env_wrapper.py`, which reads the names it needs from the local `.env` and starts the server with them, so the secret never becomes text in a config file.
5. **Permissions and hooks.** Deny reading `.env`, force pushes, history rewrites and bulk deletes in `.claude/settings.json`. Infrastructure tools never auto-approve a write.
6. **Git and GitHub.** Protect `main`, require the checks, squash merges only, the PR template with a record.
7. **Orchestration.** One writer per set of files; a worktree per change; read-only helpers for fan-out (`docs/standards/multi-agent.md`).
8. **Verifiers.** The reviewer agents and the checks run before anyone says "done" (`docs/standards/verification.md`).

## MCP credentials: the rules

| Rule | Why |
|---|---|
| A read-only token for the agent; a write token, if any, never in an MCP config | the agent advises, it does not execute |
| A personal credential where the system has one | audit and revoke per person |
| Secrets in the environment or a local `.env`, never in `mcp.json` or the client's settings | config files get shared, synced and pasted |
| A wrapper with no shell and no dependency | `shell: true` and string commands are how arguments turn into injections |
| Check whether a tool can echo secrets before calling it | some infrastructure tools return environment variables in plain text |
| Never check a variable by printing it | test existence with a boolean |

## What goes in a request, and what is already in the repository

A good request to an agent carries only what the repository does not: the goal, the decision it supports, the constraints of this task and what done looks like. Definitions, rules, standards and procedures are already loaded or one link away; repeating them in the request makes them drift.

## Environment ready

- [ ] The lakehouse builds and `python -m pytest` passes
- [ ] `make check` (or the scripts in `tools/`) passes
- [ ] The pre-commit hook runs the leak check
- [ ] The MCP servers you use start from the template without a literal secret anywhere
- [ ] `.claude/settings.json` denies reading `.env`
