# Run catalog

Everything that runs, generated from `catalog/*.yml` by `python tools/catalog.py page`. Do not edit by hand. Live health is in `observability/logs/job-health.json`, written by the collector, and the agent reads it with `get_map("jobs")`.

| Item | Kind | Situation | Owner | Trigger | Writes | AI | Status from |
|---|---|---|---|---|---|---|---|
| [Run catalog collector](../catalog/catalog-collect.yml) | job | active | RevOps lead | schedule, 08:00, 13:00 and 18:00 UTC | job health file and Slack alerts (simulated) | none | catalog-collect.yml |
| [Closed-won provisioning](../catalog/closed-won-provisioning.yml) | automation | manual | Customer Success | a deal enters closed_won (run by hand here) | one workspace request (simulated) | none | provisioning-*.md |
| [Weekly funnel review](../catalog/funnel-review.yml) | automation | manual | RevOps lead | by hand; not scheduled while the data has a fixed date | a report file | the agent half (never run) | funnel-review-*.md |
| [Lead routing](../catalog/lead-routing.yml) | automation | manual | RevOps lead | a new lead event (run by hand here) | the lead owner (simulated) | none | lead-routing-*.md |
| [Read-only MCP server](../catalog/mcp-server.yml) | server | manual | RevOps lead | started by an MCP client | nothing | none | none |
| [On-call agent](../catalog/oncall.yml) | agent | active | RevOps lead | after every collection | pull requests on oncall/<id> and reruns of rerun_ok workflows (both off until enabled) | claude-sonnet-5-5 through Claude Code, only when a problem exists (never run) | oncall.yml |
| [Revenue snapshot page](../catalog/revenue-snapshot.yml) | app | manual | RevOps lead | by hand | nothing | none | none |
| [RevOps agent](../catalog/revops-agent.yml) | agent | manual | RevOps lead | a question | nothing | claude-haiku-5-5 and claude-sonnet-5-5 (never called) | agent.jsonl |
| [Slack alerts](../catalog/slack-alerts.yml) | job | manual | RevOps lead | called by the collector and the audits | one message per finding (simulated) | none | slack-*.md |
| [Watchdog](../catalog/watchdog.yml) | job | active | RevOps lead | schedule, daily 09:30 UTC | reruns of rerun_ok workflows (off until enabled) | none | watchdog.yml |
| [Weekly data-quality audit](../catalog/weekly-audit.yml) | automation | active | RevOps lead | schedule, Mondays 07:00 UTC | a report artifact | none | weekly-audit.yml |
