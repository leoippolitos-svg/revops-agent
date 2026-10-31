# RevOps agent: context

## Summary
Every piece of the agent is built and tested, none has run with a real model. Since 2026-10-31 the repository is being brought to parity with the owner's original agent: context by area first, then the agent mechanisms (prompt blocks, category profiles, map tool, cost log, write-back controls, run catalog, on-call agent, verification).

## Session history

- **Digest, date:** 2026-10-31 (parity)
- **Context:** the owner asked that the original agent be the rule and that nothing be forgotten.
- **What was done:** PRs #49 to #61: context by area; the agent manual, security policy, session closing, workspace and memory; app standard and template, engineering security rules, team process; four-block prompt, category profiles, router cascade, answer rules; the map tool and cost per answer; write controls; run catalog, job health and Slack; on-call agent and watchdog; verification; audit pattern, reconciliation and duplicate queue; retrieval by category and reingest; business skills and lessons; README and this parity check.
- **Result:** every item of the parity list is built and tested, except what needs a host, a key or the original business (the web chat, real CRM mirrors, tool-specific flows).
- **Decision:** the web chat waits for a host and a key (ADR-0022).
- **Open items:** in `BACKLOG.md`: run with a real key, switch on Slack, the on-call agent and the AI review, host the chat.
- **Where the detail is:** records dated 2026-10-31.
- **Catalog:** 13 cards; the collector, the on-call agent, the watchdog and the weekly audits are scheduled.

- **Digest, date:** 2026-10-31
- **Context:** the owner shared the documentation of the original agent and asked for it to be the rule.
- **What was done:** read the reference design and listed every gap; added the company, area, metrics, CRM-map and rule documents (#49); wrote the agent manual with the reading order, the agent security policy, session closing, the workspace and memory.
- **Result:** the knowledge layer now has the same shape as the original: company, OKRs, entities, seven areas, metrics per area, CRM and data maps, reports, rules.
- **Decision:** recreate concepts in our own code and words, never copy files; no employer name, field key or product name enters the repository.
- **Open items:** the agent mechanisms and operations listed in `BACKLOG.md` and in the pull requests that follow.
- **Where the detail is:** records from 2026-10-31.
- **Catalog:** nothing runs on a schedule yet besides the weekly audit.
