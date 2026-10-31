---
name: session-closing
description: "Closes a work session so nothing learned is lost: picks the destination of each finding, writes the project digest, decides every scratch file and runs the exit test. Use when a task, analysis or investigation ends, before a final report, or when the user says wrap up, close the session or we are done."
---

# Session closing

Procedure and template: the `session-closing` context document.

## Steps

1. List what the session produced: rules, findings, decisions, open items.
2. Send each to its destination: a stable rule to `context/`, the story to `projects/<name>/CONTEXT.md` (create the project if none fits), a decision the agent must treat as final to `memory/decisions/`.
3. Write the digest with the template, newest first.
4. Decide every scratch file: promote, keep as listed open work, or delete.
5. Update the run catalog card if something that runs changed.
6. Run the exit test: could a new agent, reading only what is committed, tell what was done, why and what is open? If not, go back to step 2.

## Example

After an analysis of new MRR: the result is in `analyses/`, the digest in the agent project, no rule changed, no scratch left.

## Troubleshooting

- **"Too small to record"**: not a reason. Recording is cheap; losing it is expensive.
