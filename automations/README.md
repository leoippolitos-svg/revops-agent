# Automations

Every automation is Python in this folder, documented by its `SPEC.md` under [docs/standards/automations.md](../docs/standards/automations.md): the problem, why it exists as a process, the expected gain with its calculation, a diagram of how it works, where AI enters, tokens and cost, monitoring, and then its trigger, rules and limits. Audits also follow [docs/standards/audits.md](../docs/standards/audits.md). Writes go through the shared controls in `_lib/controls.py` and must be authorised in the write-back rules. Why code and not a workflow tool: [ADR-0024](../docs/adr/0024-automations-are-code-in-the-repository-not-a-workflow-tool.md).

## Index

Gains are **projections on fictional volumes**, with their assumptions in each spec.

| Automation | Trigger | Goal | Expected gain | AI |
|---|---|---|---|---|
| [`lead-routing/`](lead-routing/SPEC.md) | a new MQL event | assign the lead by segment, continuity and capacity | about 160 lead-hours of waiting a month removed | no |
| [`closed-won-provisioning/`](closed-won-provisioning/SPEC.md) | a deal enters closed won | request the workspace and the kickoff once per deal | onboarding starts 2 days earlier; 3 hours a month | no |
| [`audits/`](audits/SPEC.md) | Mondays | count data-quality flags and say what rose | about 3 hours a month; issues caught a week earlier | no |
| [`reconciliation/`](reconciliation/SPEC.md) | Mondays | list won deals that do not match billing, with owner and proposal | revenue gaps found 3 weeks earlier | no |
| [`duplicate-companies/`](duplicate-companies/SPEC.md) | Mondays | queue duplicate groups for a person to decide | 1.5 hours a week; zero automatic merges | no |
| [`onboarding-advance/`](onboarding-advance/SPEC.md) | a product event | move the onboarding milestone when the evidence arrives, with a movement log | 2 hours a month; the board accurate to the day | no |
| [`churn-deactivation/`](churn-deactivation/SPEC.md) | daily | switch off churned workspaces after the grace period, mark the company inactive | about $1,000 a month of free usage closed | no |
| [`deal-amount/`](deal-amount/SPEC.md) | a discount change | propose the new net amount for Finance to approve | 3 fewer wrong amounts a month | no |
| [`funnel-review/`](funnel-review/SPEC.md) | by hand | name the funnel stage that moved most | about 8 hours a month of analyst time | the cause step (never run) |

Every automation has a card in [`catalog/`](../catalog) and appears in [docs/run-catalog.md](../docs/run-catalog.md).
