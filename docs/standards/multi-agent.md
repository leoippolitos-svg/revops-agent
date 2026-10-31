# Working with several agents

How to run several AI agents on this repository at once without one stepping on another, and how to delegate a piece of work so it comes back usable.

## Three levels of parallelism

| Level | What | Use it for |
|---|---|---|
| Subagents | short read-only helpers inside one session, results return to it | searching, reading many files, testing one hypothesis each, reviewing |
| Sessions in separate worktrees | full sessions, each on its own branch and folder | independent changes that each end in their own pull request |
| Scheduled agents | an agent step in a workflow, such as the on-call agent | work that must happen without a person present |

## Rules

- **One writer per set of files.** Two agents never edit the same files; a session that may overlap another gets its own worktree.
- **A worktree per change.** A dirty tree with another subject is moved to a new worktree, never stashed into the middle of other work.
- **Fan out, fan in.** The main session splits the work, each helper returns a short structured result, the main session decides. Helpers do not decide for each other.
- **Read-only helpers by default.** A helper that only reads can share the checkout; one that writes cannot.
- **Do not parallelise** work whose steps depend on each other, a change that must land in one pull request, or anything that touches the same migration or rule.

## Delegating

A delegation prompt has:

1. **The goal** in one sentence, and what done looks like.
2. **The context it needs**, as paths, never "as discussed": a helper starts cold.
3. **The boundaries**: what it may read, what it must not change, what it must never do (writes, secrets).
4. **The shape of the answer**: for an investigation, one line per hypothesis with the query, the result and the verdict.
5. **The budget**: how far to go before reporting back.

Example: investigating a drop in fan-out. One helper per hypothesis from the investigation standard (duplication, filter, window, key, mix), each told to run read-only queries on gold and answer in one table row. The main session reads five rows and picks the next step.
