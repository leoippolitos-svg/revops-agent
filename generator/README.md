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
python generator/generate.py --seed 42           # initial load: data/raw/as_of=2025-12-31/ (gitignored)
python generator/generate.py --seed 42 --days 1  # one more day of business: a new as_of=<date> folder
python -m pytest                                  # runs tests/test_generator.py
```

Same seed, same files, byte for byte. Names come from short word lists in the script, e-mails use `example.com`, and there are no phone numbers or tax IDs.

Built so far: `crm/owners`, `crm/companies`, `crm/contacts`, `crm/deals`, `crm/deal_stage_history`, `marketing/campaigns`, `marketing/form_submissions`, `billing/subscriptions`, `billing/invoices`, `billing/payments`, `cs/onboarding_milestones`, `cs/health_scores`, `cs/tickets`. Billing and Customer Success live in `billing_cs.py`: a won deal becomes a subscription, which produces monthly invoices, payments, onboarding milestones, health scores and tickets. Nothing happens after the last day of the simulated world (`WORLD_END`).

The generator also writes `data/raw/_issues.json` (once, next to the snapshot folders), an answer key listing every data-quality issue it injected (type, table, row id). Tests and audits use it to tell a planned issue from a bug. Issues are injected after the clean data exists, using their own random generator, so a clean row never changes because of an issue. Injected: duplicate companies, deals without a company, stage dates out of order, competing MQL flags (`marketing_mql_flag` in `form_submissions`, `sales_mql_flag` in `contacts`) and subscriptions whose deal does not exist.

## Simulated time

The whole world, up to its last day (`WORLD_END`, 2026-12-31), is built from the seed. Each run writes a **snapshot** of it as of one day, like a nightly export of the source systems, into `data/raw/as_of=YYYY-MM-DD/`. That folder name doubles as the batch id for ingestion.

- The first run writes the initial load, as of the end of the first simulated year (2025-12-31).
- `--days N` adds N daily snapshots after the latest one, and a second run continues from there. A day already written is never changed.
- Rows dated after the snapshot day do not exist yet. Fields that change over time (deal stage, subscription status, invoice status, ticket close date) show their value on that day.
- Each snapshot is a full export, not only the changes. Bronze will keep every day's export, and silver will keep the latest version of each row.
