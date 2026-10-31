# Continuous learning

How a mistake today becomes automatic behaviour tomorrow, for people and for agents. No piece of it depends on someone remembering.

## The loop

1. **Name the lesson** in one sentence in the imperative: "never X", "always Y before Z".
2. **Write why** (the incident, with its date) and **how to apply it** (the concrete gesture).
3. **Choose the destination** by how far the lesson reaches (table below).
4. **Fix the state the mistake left now**, in the same turn, not at the end of the day. A tool-made inconsistency left "to align later" came back hours later in the reference design.
5. **Check at the next occurrence.** Did the rule fire? If the mistake came back, the lesson is in the wrong place: climb one step of the ladder.

## Where each lesson goes

| Reach of the lesson | Destination | Example |
|---|---|---|
| A personal preference of whoever asks | the agent's personal memory | "short reports, tables instead of stories" |
| A behaviour rule for every agent in the repository | `CLAUDE.md` or a standard it links | "never read `.env` with a shell command" |
| A stable fact about data or a system | a context document | "this table is a change log: latest version before any join" |
| A procedure that repeats | a skill | "diagnosing a number that does not match" |
| A costly conclusion that must not be redone | `memory/decisions/` or a decision record | "these thresholds were accepted; do not reopen without new data" |
| Something a script can check | a test, a lock in a script, a check in `tools/` | "fail if revenue moves more than 2% from the anchor" |
| Security that a machine can verify | a blocking CI check | "a secret in the diff" |
| A process obligation | the session-closing steps, or the skill that creates the thing | "register every new job in the run catalog" |

## The ladder of strength

Climb one step when a lesson does not hold:

| Step | Mechanism | Holds when | Fails when |
|---|---|---|---|
| 1 | Personal memory | one person, one machine | anyone else does the work |
| 2 | A document in the repository | people read it | nobody opens it at the right moment |
| 3 | A rule loaded in every session (`CLAUDE.md`) | the agent follows instructions | the context is long and the rule is buried |
| 4 | A skill or checklist in the flow | the flow is followed | the step is skipped |
| 5 | A script or test | it runs | it is not run |
| 6 | A blocking CI check | always | the team rejects it; then the rule was wrong, not weak |

Not every lesson belongs at the top. In the reference design a team rule turned into a blocking CI check was rejected by the team; it went back to the session-closing checklist, which held.

## Anti-patterns

- Writing the lesson only in the conversation.
- A rule with no "why": nobody can tell when it no longer applies.
- Fixing the symptom and not the place that let it happen.
- Ten rules where one check would do.

## Turning a correction into a rule

When a person corrects an answer, the agent (or the analyst) writes: the lesson in one imperative sentence, the incident and its date, the destination from the table, and the change itself in a pull request. A corrected definition is a `context` pull request; the correction loop in the README is this.
