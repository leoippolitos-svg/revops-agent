---
name: new-micro-app
description: Scaffolds a micro-app in apps/ following the spec-driven flow and the security checklist. Use when the user asks for a "micro-app", "internal tool", "small app", "form" or "dashboard app" for the revenue team.
---

# New micro-app

## Steps

1. **Research**: who uses it, which decision it supports, which gold tables it needs. Write it down.
2. **Spec**: copy `apps/_template/` to `apps/<app-name>/` and fill `SPEC.md` (problem, users, screens, data read, what it must never do). Commit the spec before any code.
3. **Implement** the smallest version that answers the spec. Read data only from gold, read-only.
4. **QA**: test the main path and two failure paths (empty data, invalid input).
5. **Security**: go through every item of the micro-app checklist in `docs/standards/security.md` and paste the ticked list into the PR.
6. **Register** any new connection in `connectors/registry.yaml`.
7. Open an `app` PR with `open-pr`.

## Never

- Add write access to a data source without an ADR.
- Put a key or token in front-end code.
