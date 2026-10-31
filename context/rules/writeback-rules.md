---
id: writeback-rules
title: Write-back rules
kind: rule
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [lead-routing, closed-won-provisioning, crm-map]
---

# Write-back rules

## Purpose

The single list of what may be written into another system, by which automation, and under which controls. The agent reads it to answer "can you change X?" (the answer is always no from the agent, and here is who can) and every automation is checked against it. It does not describe how an automation works; that is its spec. RevOps owns it; a new write needs a decision record and a change here in the same pull request.

## Rules

1. **The agent never writes.** Chat, skills and the MCP server are read-only. They recommend, a person or an automation acts.
2. **Writes happen only in deterministic automations**, with no model in the step that writes.
3. **Only the fields in the table below may be written.** Anything else is forbidden, even if a person asks.
4. **Every write is logged** with the previous value, the new value, the time, the automation and the reason. Nothing is overwritten without history.
5. **A conflict stops the write.** If the target changed since it was read, or the change is beyond the field's threshold, nothing is written, the conflict is logged and a person reviews it.
6. **Reversal** is documented: read the log, take the previous value, write it back by hand with a note.

### Fields that may be written

| System | Object and field | Automation | Authorization | Decision | Cap per run |
|---|---|---|---|---|---|
| CRM | the owner of a new lead | `lead-routing` | recurring | ADR-0010 | 50 |
| Product | one workspace and its onboarding kickoff per signed deal | `closed-won-provisioning` | recurring | ADR-0011 | 20 |
| Slack | one alert message per finding, in the alerts channel | `slack-alerts` | recurring | ADR-0020 | 30 |

The cap is read by the automation at run time: past it, the rest of the run waits for review. Each automation writes only when its kill switch, `<NAME>_ENABLED=true` (for example `LEAD_ROUTING_ENABLED`), is set; without it a `--write` run is a shadow run.

### Authorization levels

- **Recurring authorization**: the automation may write on every run within the scope above. The section that grants it carries the marker `RECURRING-AUTHORIZATION: <automation>`, its scope and what is out of scope. Turning the automation off removes the marker in the same pull request.
  - RECURRING-AUTHORIZATION: lead-routing. Scope: the owner of a new lead. Out of scope: any other field, any existing owner change beyond the routing rule.
  - RECURRING-AUTHORIZATION: closed-won-provisioning. Scope: one workspace request and one kickoff request per signed deal. Out of scope: plan, price, users, and anything for a deal that is not closed won.
  - RECURRING-AUTHORIZATION: slack-alerts. Scope: one message per finding in the alerts channel, text built by code, one thread per item. Out of scope: direct messages, any other channel, any text written by a model.
- **Proposal and approval**: for a sensitive field (an amount, a status that affects billing), the automation only writes a proposal. A person approves item by item, never in bulk, and a separate manual step applies it with the approver's name and the previous value.
- **Forbidden**: everything not listed.

### Controls every writing automation has

Dry run by default; a kill switch that turns writes off without a deploy; a cap of writes per run; a circuit breaker that stops the run after consecutive failures; an idempotency key so a rerun never writes twice; a match only on an explicit id, never on a name; a review queue for anything unmatched or failed, reported as "needs review" and never as "skipped"; a check after writing that re-reads the target; and a date cutoff so old records are never back-filled silently.

## Owner and approvers

RevOps owns this list. A new field, system or automation needs a decision record and RevOps approval in the pull request; a sensitive field also needs the owner of that data (Finance for amounts, Customer Success for accounts).
