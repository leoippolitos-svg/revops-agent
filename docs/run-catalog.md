# Run catalog

Everything that runs, generated from `catalog/*.yml` by `python tools/catalog.py page`. Do not edit by hand. Live health is in `observability/logs/job-health.json`, written by the collector, and the agent reads it with `get_map("jobs")`.

| Item | Kind | Situation | Owner | Trigger | Writes | AI | Status from |
|---|---|---|---|---|---|---|---|
| [Agent chat (local demo)](../catalog/agent-chat.yml) | app | manual | RevOps lead | by hand | nothing | none in demo mode; the agent's models with --model (never run) | none |
| [Run catalog collector](../catalog/catalog-collect.yml) | job | active | RevOps lead | schedule, 08:00, 13:00 and 18:00 UTC | job health file and Slack alerts (simulated) | none | catalog-collect.yml |
| [Deactivation after churn](../catalog/churn-deactivation.yml) | automation | active | Customer Success | schedule, daily 06:00 UTC | workspace access and company status (simulated), movement log | none | daily-automations.yml |
| [Closed-won provisioning](../catalog/closed-won-provisioning.yml) | automation | manual | Customer Success | a deal enters closed_won (run by hand here) | one workspace request (simulated) | none | provisioning-*.md |
| [Deal amount recalculation](../catalog/deal-amount.yml) | automation | manual | Sales | a discount change (run by hand here) | a proposals file; never the CRM | none | amount-proposals-*.md |
| [Duplicate companies review queue](../catalog/duplicate-companies.yml) | automation | active | RevOps lead | schedule, Mondays, in the weekly audit workflow | a review queue file | none | weekly-audit.yml |
| [Account review narrative](../catalog/ebr-narrative.yml) | automation | manual | Customer Success | by hand, before a review | a briefs file | claude-haiku-5-5 through ai_step (demo without a key) | ebr-briefs-*.json |
| [Weekly funnel review](../catalog/funnel-review.yml) | automation | manual | RevOps lead | by hand; not scheduled while the data has a fixed date | a report file | the agent half (never run) | funnel-review-*.md |
| [Lead routing](../catalog/lead-routing.yml) | automation | manual | RevOps lead | a new lead event (run by hand here) | the lead owner (simulated) | none | lead-routing-*.md |
| [Read-only MCP server](../catalog/mcp-server.yml) | server | manual | RevOps lead | started by an MCP client | nothing | none | none |
| [Onboarding auto-advance](../catalog/onboarding-advance.yml) | automation | manual | Customer Success | a product event (run by hand here) | the onboarding milestone (simulated) and the movement log | none | movements-*.md |
| [On-call agent](../catalog/oncall.yml) | agent | active | RevOps lead | after every collection | pull requests on oncall/<id> and reruns of rerun_ok workflows (both off until enabled) | claude-sonnet-5-5 through Claude Code, only when a problem exists (never run) | oncall.yml |
| [Proposal generator](../catalog/proposal-generator.yml) | automation | manual | Sales | a seller asks for a proposal (run by hand here) | a drafts file; never the CRM | claude-haiku-5-5 through ai_step (demo without a key) | proposals-*.json |
| [Prospecting drafts](../catalog/prospecting-drafts.yml) | automation | manual | Sales | a new lead with a qualification (run by hand here) | a drafts file; never the CRM, never a message | claude-haiku-5-5 through ai_step (demo without a key) | prospecting-drafts-*.json |
| [Deal and subscription reconciliation](../catalog/reconciliation.yml) | automation | active | RevOps lead | schedule, Mondays, in the weekly audit workflow | a report and a Slack alert (simulated) | none | weekly-audit.yml |
| [Revenue snapshot page](../catalog/revenue-snapshot.yml) | app | manual | RevOps lead | by hand | nothing | none | none |
| [RevOps agent](../catalog/revops-agent.yml) | agent | manual | RevOps lead | a question | nothing | claude-haiku-5-5 and claude-sonnet-5-5 (never called) | agent.jsonl |
| [Site qualification](../catalog/site-qualification.yml) | automation | manual | Sales | a qualification request (run by hand here) | the qualification field (simulated) | claude-haiku-5-5 through ai_step (demo without a key) | site-qualification-*.json |
| [Slack alerts](../catalog/slack-alerts.yml) | job | manual | RevOps lead | called by the collector and the audits | one message per finding (simulated) | none | slack-*.md |
| [Watchdog](../catalog/watchdog.yml) | job | active | RevOps lead | schedule, daily 09:30 UTC | reruns of rerun_ok workflows (off until enabled) | none | watchdog.yml |
| [Weekly data-quality audit](../catalog/weekly-audit.yml) | automation | active | RevOps lead | schedule, Mondays 07:00 UTC | a report artifact | none | weekly-audit.yml |
