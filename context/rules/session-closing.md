---
id: session-closing
title: Session closing
kind: process
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [agent-security]
---

# Session closing

## Purpose

Makes sure no work session ends without the knowledge it produced being written into the repository, and gives the digest template. Every person and every agent reads it at the end of a task, analysis, investigation or decision, with or without code changes: the record is about knowledge produced, not files touched. The content of digests does not go here; it goes in the project folder. RevOps owns it and changes it only when the team changes how work is recorded.

## Steps

1. **Pick the destination** of what was learned:
   - a **context document** for a stable fact: a data rule, a join, a metric definition, a system behaviour. Context is timeless.
   - a **project digest** in `projects/<project>/CONTEXT.md`, under "Session history", for an investigation, analysis, decision or finding that is not a stable rule. A digest is history.
   - a **new project folder** with a minimal `CONTEXT.md` when the work has no project yet. "Too small to record" is not a reason: recording is cheap, losing it is expensive.
2. **Write the record** of every pull request in `records/`, as the pull-request standard requires.
3. **Decide every scratch file** touched in the session: promote it (code, skill, context, digest), keep it as open work and list it as a pending item in the digest, or delete it now.
4. **Update the run catalog** if something that runs was created, changed or stopped.
5. **Run the exit test**: could a new agent, reading only what was committed, tell what was done, why, and what is still open? If not, the session is not closed.

## Template

Copy into the "Session history" section of the project's `CONTEXT.md`:

- **Digest, date:** YYYY-MM-DD
- **Context:** what started this work, in one or two sentences.
- **What was done:** the investigation, analysis or change, with the method in brief.
- **Result:** the main finding, with the number if there is one.
- **Decision:** what was decided or published as a consequence.
- **Open items:** what is still unanswered or needs a next step, with an owner.
- **Where the detail is:** files, pull requests, records.
- **Catalog:** the card created or updated, or "nothing runs".

A good example is the funnel review project, whose digest says what was built, what was assumed and what is still waiting on the owner.
