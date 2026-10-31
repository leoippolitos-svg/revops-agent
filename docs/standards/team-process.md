# Team process

How people and AI agents work in this repository. The pull-request rules are in [pull-requests.md](pull-requests.md); this page is the cycle around them and the habits that keep the work honest. Every principle below came from a correction made to an agent or a person in the reference design.

## The cycle of every task

1. **Read the context first.** Business question: the agent's reading order (`agent/directives/AGENT.md`). Code or infrastructure: the standards and the spec.
2. **Spec before code.** Anything that runs, writes or is used by others starts as a spec (app, automation) or a short plan in the project's `CONTEXT.md`, reviewed before the first line of code.
3. **Branch** named `<type>/<short-description>`, never work on `main`.
4. **Build the smallest version**, with its tests.
5. **Verify independently**: whoever builds does not check alone. A second agent or a script tries to break the result: the `adversarial-reviewer` and `done-verifier` subagents in `.claude/agents/`, the `pr-review` skill and [verification.md](verification.md).
6. **Close the session** (context document `session-closing`) and open the pull request with its record.

### Who approves

- Context documents, routing, skills and automations: RevOps admin.
- A new write to any system, a new dependency or a new agent tool: a decision record plus RevOps admin.
- Nobody approves their own pull request; on a solo repository the author's review is labelled as such.

## Six laws of git

1. **Never commit to `main`.** Every change is a pull request, merged by squash.
2. **CI runs on every pull request.** Path filters may skip slow jobs, never the secret scan.
3. **Only porcelain git, and check by reading back.** After a commit or merge, read the log or the file; never assume.
4. **No history rewrite without asking, every time.** No force-push, no amend of a pushed commit.
5. **Start from the tip.** A branch behind `main` is rebased, or a new branch is cut from the tip, before committing.
6. **Deploys follow a tag, not `main`.** What runs in production is a named version that can be rolled back.

### Habits that go with them

- **Dirty tree with another subject?** Use a separate worktree instead of stashing and mixing.
- **Conventional, imperative commit titles**: `automation: route leads by segment`.
- **One subject per pull request**, small enough to review in one sitting.
- **Whose repository is it?** Check the remote before any push; another team's repository is read, not written: deliver the list of what should change.
- **Derived files**: a short copy of a long source (a summary of the security rules) declares its source; `tools/check_derived.py` warns when the source changed, and the copy is updated in the same pull request.

## Green is not reviewed

Green checks say the checks passed, nothing more. In the reference design an AI security review passed on the pull request and reported two high findings only after the merge. So: changes to authorisation, grants or writes are reviewed by hand against the security rules before asking for a merge, and the post-merge result is read.

## Working principles

### Communication and reports
1. **Say less.** The answer first; a table instead of a story; root cause only when it changes the action.
2. **Write in the present.** No "before it was", "fixed from X to Y": the reader never saw the old version.
3. **Complete tables.** Every expected column and segment is shown; a missing value is a visible "n/a", never a silent gap.
4. **Always a time series.** A comparison comes with its history, the current period labelled partial and any projection labelled with whose it is.
5. **A pending human action is an exact address**: screen, menu, field, expected value and how to confirm it, never "configure the OAuth".

### Context and scope
6. **Read the context before answering a data question.** Skipping the reading order mixes definitions and ignores access rules.
7. **Touch only what is yours.**
8. **Before saying "I have no access", check the mechanism**: a newly enabled connector may only appear after restarting the session.
9. **Use full model ids**, never aliases, and check which runtime actually runs the agent.

### Operational safety
10. **Never read `.env` with a shell command**; check existence with a boolean. If a value leaks, say so at once without repeating it, and rotate.
11. **Green is not reviewed** (above).
12. **A deploy status can belong to the previous deploy**; wait for the new deploy id.
13. **Fix inconsistencies in the same turn** they appear, not at the end of the day.

### Data and mirrored systems
14. **Do not filter freshness by sync timestamp** when the writer became incremental.
15. **An incremental watermark comes from its own checkpoint**, never from the table's maximum, which any other writer can push.
16. **A "primary" association holds one value**; many-to-many needs the association table. Decide which one is used for money and which for signals.
17. **Production code may not match the repository**; read the deployed version before trusting an analysis of it.
18. **A parent entity referenced by many tables is never deleted**, and jobs get no delete grant on it.
19. **A field overwritten by a periodic import** loses manual fixes; fix it at the source.
20. **Anchor before modelling**: fix and record the validated business anchors before projecting, so no factor is counted twice.
