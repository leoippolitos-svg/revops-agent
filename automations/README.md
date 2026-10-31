# Automations

Every automation is Python in this folder, documented by its `SPEC.md` under [docs/standards/automations.md](../docs/standards/automations.md): the problem, why it exists as a process, the expected gain with its calculation, a diagram of how it works, where AI enters, tokens and cost, monitoring, and then its trigger, rules and limits. Audits also follow [docs/standards/audits.md](../docs/standards/audits.md). Writes go through the shared controls in `_lib/controls.py` and must be authorised in the write-back rules. A step that uses a model goes through `_lib/ai_step.py`: the prompt is a file here with its hash recorded in the spec (checked by `tools/check_prompts.py`), the output is validated in code, and tokens and cost are logged per run in `observability/logs/ai-steps.jsonl`. Why code and not a workflow tool: [ADR-0024](../docs/adr/0024-automations-are-code-in-the-repository-not-a-workflow-tool.md).

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
| [`site-qualification/`](site-qualification/SPEC.md) | a qualification request | read a company's website and write a validated summary for the SDR | 4 hours a month of SDR research | yes: fast model, validated JSON, quotes checked against the site |
| [`prospecting-drafts/`](prospecting-drafts/SPEC.md) | a new lead with a qualification | draft a first touch and a follow-up from evidence-backed arguments; never sends | about 10 hours a month of SDR writing | yes: fast model, only eligible arguments reach it, forbidden claims rejected in code |
| [`proposal-generator/`](proposal-generator/SPEC.md) | a seller asks for a proposal | extract facts from the meeting note and assemble the draft in code | about 6 hours a month of seller writing | yes: the model only extracts facts, checked against the note |
| [`ebr-narrative/`](ebr-narrative/SPEC.md) | before an executive review | a brief for the CSM from gold, numbers checked | 5 hours a month of preparation | yes: prose only, every number must be in the data pack |
| [`funnel-review/`](funnel-review/SPEC.md) | by hand | name the funnel stage that moved most | about 8 hours a month of analyst time | the cause step (never run) |

Worked examples documented to the standard but not built are in [`_examples/`](_examples/README.md), starting with a multi-year contract split.

Every automation has a card in [`catalog/`](../catalog) and appears in [docs/run-catalog.md](../docs/run-catalog.md).
