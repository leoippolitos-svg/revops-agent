---
derived_from: docs/standards/security.md
source_sha256: bdfa18a8e042fe7ca5fac82e0745abf68fd2e69dd35f6db6bd608f20527984a0
---

# Security in one page

A condensed copy of [security.md](security.md) for quick reading. The source wins; `tools/check_derived.py` warns when the source changed and this page was not updated.

- The agent advises, it does not execute: read-only everywhere, no writes, no messages.
- Rules are enforced outside the model: read-only connections, denied commands, CI checks.
- Least privilege for every connector, recorded in `connectors/registry.yaml`.
- Rule zero: nothing real from any employer or client; the leak check runs before every commit and in CI.
- Secrets only in `.env` (gitignored) or CI secrets; never read `.env` with a shell command.
- Authorisation on the server; sessions in HttpOnly cookies; inputs validated; no IDOR (404).
- One door to the data (`query_gold`); one credential per app; admin credential only in jobs.
- Server-side requests only to allowlisted hosts; AI on the server, no personal data in prompts or logs.
- Errors: full detail in the server log, generic message to the user; never log a connection error object.
- New app: from the template, through the playbook in [apps.md](apps.md), before the first deploy.
- Green checks are not a security review; authorisation and grant changes are read by hand.
- If a request breaks a rule: name the rule, propose the safe alternative, never build it "to test".
