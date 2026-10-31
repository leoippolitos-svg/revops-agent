# Lessons learned

Lessons from running a RevOps agent, its automations and its apps in production, rewritten without any company detail. Each one is situation, cause, fix, and the rule it left in this repository. New lessons are added through the loop in [continuous-learning.md](standards/continuous-learning.md).

## Infrastructure and data stores

**A shared database went down under a file load.** Situation: apps and jobs shared one database; a bulk file load saturated it and every app failed at once. Cause: no limit on what one job could consume. Fix: the load ran in batches off-hours. Rule: before changing a job's volume or permissions, measure what it already uses and grants (team-process, operational safety).

**"The terminal was aborted" did not mean the job died.** Situation: a long job looked stopped and was started again, and two copies wrote at once. Cause: the job kept running on the server after the terminal closed. Fix: check the job list before restarting. Rule: idempotent writes keyed on an explicit id, so a second copy changes nothing (write controls).

## Secrets and security

**Reading `.env` with a shell printed a password.** Situation: a quick shell command to check a variable printed connection strings. Cause: lines without `=` are printed whole. Fix: rotate at once. Rule: check that a variable exists with a boolean, never read `.env` (security, rule 10 of the team principles).

**An invalid connection URL logged the whole connection string.** Cause: the error object carries the URL. Rule: log the message only, never the error object, in code that builds a connection from a URL (security, rule 20).

**Green checks were not a security review.** Situation: an AI review passed on the pull request and reported two high findings only after merge. Rule: authorisation and grant changes are read by hand; the post-merge result is read too (verification).

## Deploy and CI

**A "done" status belonged to the previous deploy.** Rule: wait for the new deploy id before saying something is live (apps standard).

**A team rule turned into a blocking CI check was rejected by the team.** Cause: the rule was a process obligation, not something a machine can judge. Fix: it went back to the session-closing checklist. Rule: not every lesson belongs at the top of the ladder (continuous-learning).

## Mirrors and integrations

**A CRM mirror had five traps at once.** Search APIs that stop paginating at a fixed ceiling, huge pipelines mirrored only for active stages, an owners table needed to name people, progress tracked by checkpoint and not by sync time, and a new view that inherited write grants. Rule: say when a base is truncated instead of computing a rate on it; give jobs their own checkpoint (team principles 14 and 15).

**A connector "did not exist"; it was only not loaded yet.** Rule: before saying "no access", check the mechanism; a new connector may need a session restart (team principle 8).

## Data and metrics

**An "active" status rewrote the past.** Situation: a monthly count used today's status for every past month. Rule: compute history with the status on the event date (investigation hypotheses: status).

**Revenue counted twice.** Cause: a change log kept several versions per record and the join ran before taking the latest. Rule: latest version per key before any join (investigation hypotheses: duplication).

**The same mistake three times: an aggregate without its list of ids.** Rule: every difference between sources becomes a list of records, each classified (audits standard).

**A "false zero" from a label that did not exist.** Cause: a filter on a literal value the data never held returned zero rows, which looked like a real zero. Rule: list the distinct values of a field before filtering on it.

**A "62% drop" was a change in portfolio.** Cause: the mix of what was sold changed, not the rate. Rule: split a change into mix and rate before calling it a decline (investigation hypotheses: mix).

**A health score had half its weight without a source.** Rule: a composite metric states which components are missing and labels itself partial (metrics documents: "not in gold yet").

## CRM, reconciliation and automated writes

**Revenue in the CRM and in finance did not match.** Rule: billing is the source of truth for revenue; the CRM is corrected, never the other way round (cross-cutting-rules).

**A contract was linked to the wrong deal.** Cause: matching by company name. Rule: match only on an explicit id; anything unmatched goes to a review queue, never a guess (write-back rules, audits).

**Merging duplicate companies could not be undone.** Rule: merges are proposals approved group by group by a person; nothing merges automatically (duplicate-companies automation).

## Working with AI agents and the team

**The process lived where the team did not read it.** Rule: the process is in the repository the agent loads every session, and in the skills that run the steps (CLAUDE.md, session-closing).

**A vague pending item for a person was never done.** Rule: a human step is an exact address: screen, menu, field, expected value (team principle 5).

**What to index for retrieval was decided by the eval.** Situation: a question kept failing because its answer lived in a file outside the corpus. Rule: retrieval failures change the corpus or the expected answer, recorded with the eval (RAG standard).

**Access by role versus an allowlist.** Filtering content per role failed silently; an allowlist at the door failed visibly and reversibly. Rule: decide access at the door (security, rule 10).

## What I would do differently

- Start with the context layer and the evaluation, before the chat interface.
- Write every recurring write as an automation with a spec and a kill switch from day one.
- Keep one catalog of everything that runs from the first job, not after the tenth.
