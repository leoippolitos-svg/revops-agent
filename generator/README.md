# Generator

Creates fictional raw data for the lakehouse. Phase 1.

## The fictional company: Fernway

Fernway sells field-service management software (scheduling, work orders, mobile app for technicians) to mid-size maintenance and facilities companies. Any resemblance to a real company is coincidental.

| Team | Owns | Key stages and metrics |
|---|---|---|
| Marketing | Demand generation | Leads, MQLs, cost per MQL |
| SDR | Qualification | MQL → SQL, speed to lead |
| Sales | SMB and mid-market deals | Opportunities, win rate, cycle time |
| Enterprise | Large accounts | Pipeline coverage, proposal stage |
| Onboarding | Implementation | Time to go-live, activation |
| Customer Success | Retention and expansion | Health score, churn, NRR |
| RevOps | Data, process, tooling | Data quality, forecast accuracy |

## Sources

| Source | Objects |
|---|---|
| CRM | companies, contacts, deals, deal stage history, owners |
| Marketing forms | form submissions, campaigns |
| Billing | subscriptions, invoices, payments |
| Customer Success | health scores, tickets, onboarding milestones |

## Deliberate data-quality issues

So that audits and the agent have something real to catch: duplicate companies, deals without a company association, stage dates out of order, a subscription with no matching deal, and two competing MQL flags (one set by Marketing, one by Sales).

## Simulated time

`generate.py --days 1` adds one more day of business, so the pipeline can run on a schedule like a real lakehouse.
