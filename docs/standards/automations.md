# Automations

How an automation is specified and documented here. Every automation has a `SPEC.md` that a person who never saw the code can read in five minutes and answer: what problem does this solve, why does it exist as a process, what does it gain, how does it work, where does AI enter, what does it cost, and how do we know it is working. The `new-automation` skill follows this standard and `tools/check_automations.py` checks the sections.

## Why automations live here and not in a workflow tool

The reference design ran many of its flows in n8n. That worked, and it cost: the prompt running in the tool drifted from the one in the repository, some flows existed only in the tool's instance, and moving them between accounts was a project of its own. Here an automation is Python in this repository, scheduled by GitHub Actions, with tests, the shared write controls, rules read from the context documents and a pull request for every change ([ADR-0024](../adr/0024-automations-are-code-in-the-repository-not-a-workflow-tool.md)). A workflow tool is still a good choice for teams that do not write code or that glue many SaaS tools; the patterns below apply there too.

## The sections of a spec

| Section | What it must say |
|---|---|
| **Problem** | What goes wrong today, for whom, and how often. Concrete. |
| **Why this process** | Why an automation and not a person, a report or a rule in a document. What would happen without it. |
| **Expected gains** | The gain in time, errors or speed, **with the calculation and every assumption written down**, labelled as a projection. Fernway is fictional, so every number here is a projection on fictional volumes, never a measured result. Say how it will be measured once it runs. |
| **How it works** | A diagram (Mermaid) of the trigger, the steps, the decisions and the effects, and the steps in words. |
| **Where AI enters** | "Nowhere: it is deterministic", or the step, the model, the prompt file and its hash, the output shape the code validates, and the guardrails enforced in code (what never reaches the model). |
| **Tokens and cost** | Tokens and cost per run and per month, estimated from volume, and where they are logged. "No model call" for deterministic automations. Unknown prices are logged as null, never zero. |
| **Monitoring** | Its catalog card, its status source, its alert, and the number that shows it is delivering. |
| **Trigger, Inputs, Rules, Effects, Failure behavior, Must never** | As before: what starts it, what it reads (gold only), which context documents hold its rules, what it changes, what happens on error, what it must never do. |
| **Security checklist** | The automation checklist of the security standard, ticked only when built. |

## Patterns every automation follows

These come from the flows of the reference design, whatever tool ran them:

- **Errors are loud.** A failure stops the run with exit code 1 and writes nothing; it is never reported as success, and anything not done is "needs review".
- **Idempotent by an explicit id.** A rerun overwrites the same line; matching is on an id, never on a name.
- **Respect rate limits.** Batch, back off, and cap writes per run.
- **A trigger field and a stamp field are separate.** The field that starts a flow and the field the flow writes when it finishes are different, so an incomplete run can be found.
- **Sub-steps are shared code**, such as the movement log, so every automation records changes the same way.
- **AI never writes directly.** It produces a draft or a field the code validates; guardrails are structural (what the model never sees), not instructions in the prompt; the prompt lives in the repository and its hash is checked before an evaluation.
- **Secrets only in the environment or CI secrets**, never in a file, a log or a prompt.
