# Automations

Planned examples, except `audits/`, `lead-routing/` and `closed-won-provisioning/`, which are built, and `funnel-review/`, which is specified. Each has a spec, tests and the automation checklist from `docs/standards/security.md`. `tools/check_automations.py` validates every spec that exists:

| Automation | What it does |
|---|---|
| [`lead-routing/`](lead-routing/SPEC.md) | Assigns new leads by segment and capacity. Built (`route.py`, dry run by default); its only write is the owner field, simulated as a log line (ADR-0010) |
| [`closed-won-provisioning/`](closed-won-provisioning/SPEC.md) | On closed won, provisions the customer in the product (simulated event). Built (`provision.py`, dry run by default); its only write is one workspace request, simulated as a log line (ADR-0011) |
| [`audits/`](audits/SPEC.md) | Weekly data-quality audit over `gold.data_quality_snapshot`. Built; runs by schedule in `.github/workflows/weekly-audit.yml`, report kept as a workflow artifact |
| [`funnel-review/`](funnel-review/SPEC.md) | Weekly funnel diagnosis using the `funnel-diagnosis` skill. Specified, not built |
