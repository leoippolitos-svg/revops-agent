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

## Usage

```bash
pip install -r requirements.txt
python generator/generate.py --seed 42   # writes CSV files to data/raw/ (gitignored)
python -m pytest                          # runs tests/test_generator.py
```

Same seed, same files, byte for byte. Names come from short word lists in the script, e-mails use `example.com`, and there are no phone numbers or tax IDs.

Built so far: `crm/owners`, `crm/companies`, `crm/contacts`, `crm/deals`, `crm/deal_stage_history`, `marketing/campaigns`, `marketing/form_submissions`. Billing and Customer Success come next.

The generator also writes `data/raw/_issues.json`, an answer key listing every data-quality issue it injected (type, table, row id). Tests and audits use it to tell a planned issue from a bug. Issues are injected after the clean data exists, using their own random generator, so a clean row never changes because of an issue. Injected so far: duplicate companies, deals without a company, stage dates out of order, and competing MQL flags (`marketing_mql_flag` in `form_submissions`, `sales_mql_flag` in `contacts`).

## Simulated time

`generate.py --days 1` adds one more day of business, so the pipeline can run on a schedule like a real lakehouse.
