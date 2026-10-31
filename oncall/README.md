# On-call

What happens when something in the run catalog breaks (ADR-0021).

| File | Step | AI |
|---|---|---|
| `oncall.py problems` | lists the failing or late items of the last collection, with their cards | no |
| `prompt.md` | the agent: diagnoses each item, may open one fix pull request on `oncall/<id>`, asks for actions from a closed list, writes the human step | yes, only when a problem exists |
| `oncall.py execute` | checks the agent's report, runs only allowed reruns through the write controls, posts one Slack message per item in its thread | no |
| `watchdog.py` | daily: restarts a late job whose card says `rerun_ok`, alerts only when it cannot | no |

Workflows: `.github/workflows/oncall.yml` (after each collection) and `watchdog.yml` (daily).

Switches, all off in this repository: `ONCALL_AGENT_ENABLED` (the agent step, plus the `ANTHROPIC_API_KEY` secret), `ONCALL_ACTIONS_ENABLED` (reruns asked by the agent), `WATCHDOG_ENABLED` (reruns by the watchdog), `SLACK_ALERTS_ENABLED` (alerts, plus the `SLACK_WEBHOOK_URL` secret for a real post).
