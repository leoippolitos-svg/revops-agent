# Automations

Planned examples, except `audits/`, which is built. Each has a spec, tests and the automation checklist from `docs/standards/security.md`:

| Automation | What it does |
|---|---|
| `lead-routing/` | Qualifies and assigns new leads by segment and capacity |
| `closed-won-provisioning/` | On closed won, provisions the customer in the product (simulated event) |
| [`audits/`](audits/SPEC.md) | Weekly data-quality audit over `gold.data_quality_snapshot`. Built; runs by schedule in `.github/workflows/weekly-audit.yml`, report kept as a workflow artifact |
| `funnel-review/` | Weekly funnel diagnosis using the `funnel-diagnosis` skill |
