# Apps

Micro-apps for the revenue team. Each one starts as a copy of `_template/` and follows the `new-micro-app` skill: spec first, then code, then the security checklist.

| App | Status |
|---|---|
| [`agent-chat`](agent-chat/README.md) | Built: `python apps/agent-chat/server.py` opens a local chat that shows the agent's route, documents, prompt blocks and tools for every answer. Demo mode needs no key (ADR-0023) |
| [`revenue-snapshot`](revenue-snapshot/SPEC.md) | Built: `python apps/revenue-snapshot/snapshot.py --out page.html` writes a static page. Tested; never opened in a real browser |

`tools/check_apps.py` validates every spec: all sections present, gold tables only, writes forbidden, and a checklist item is ticked only when the app is built.
