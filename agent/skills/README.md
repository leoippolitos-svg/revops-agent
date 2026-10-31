# Business skills

Skills the RevOps agent loads to do business work. A skill named in an intent's row of `agent/directives/routing.md` loads automatically; the others are picked by the analyst (or the coding agent running the `new-analysis` skill) from the map below.

| Question looks like | Skill | Tier | Extra documents |
|---|---|---|---|
| why did conversion drop, where does the funnel leak | `funnel-diagnosis` | standard | `funnel-stages`, `crm-map` |
| how has a metric moved | `trend-analysis` | standard | the metric's document |
| why don't two numbers match | `data-discrepancy` | standard | `cross-cutting-rules` |
| build a report | `html-report` | standard | `okrs` |
| how did a cohort perform | `cohort-analysis` | standard | `funnel-stages` |
| which accounts are at risk | `detect-risk` | standard | `area-customer-success` |
| where will MRR land | `forecast-revenue` | standard | `mrr`, `okrs` |
| which deals to focus on | `score-deals` | fast | `metrics-sales` |
| a question across two sources | `cross-source-analysis` | standard | `cross-cutting-rules` |
| is a change real or noise | `statistical-check` | fast | the metric's document |
| change, approve or decide something | `escalate-to-human`, `writeback-request` | fast | `writeback-rules` |
| this keeps coming back every week | `recommend-automation` | fast | `apps`, the run catalog |
