---
name: business-health-diagnosis
description: "Diagnoses the health of a line of business in a fixed order (hygiene, funnel, retention, segments, causes, plan), calibrated against anchor numbers, with every hypothesis given a verdict. Use when someone asks how the business is really doing, why revenue is off plan, or for a full diagnosis of a product line or segment."
---

# Business health diagnosis

Method: section 9 of `docs/standards/revops-methodologies.md`. Each step inherits the universe of the step before and never redefines filters.

## Steps

0. **Hygiene**: exclude internal and test accounts, note the duplicate and orphan flags from `cross-cutting-rules`.
1. **Funnel**: volume, conversion and bookings over the periods available, calibrated against the anchor numbers (the last full month's MRR, active customers). Stop if they do not reproduce within 2%.
2. **Retention**: churned MRR, monthly churn rate by count and by value, NRR (which equals gross retention while there is no expansion).
3. **Segments**: the same by segment and industry, with n.
4. **Causes**: mix by cohort, onboarding capacity (time to go-live), pricing and discounts. Each hypothesis gets a verdict: confirmed, refuted, supported, does not exist.
5. **Plan**: which levers move the target in `okrs`, as a range.

## Rules

- One change at a time, showing its effect. No coverage: stop and report; a proxy is labelled with its coverage.
- When every group falls at the same time, the next step is a conversation with the operation, not more data.
- Record the refuted hypotheses, so they do not come back.

## Example

"How is the business doing?" Funnel calibrated against December's MRR; retention 1.9% churned MRR in the only month with churn; segments too small to split with confidence; causes: one fewer won deal explains December; plan: the target needs new MRR near the autumn pace, shown as a range.

## Troubleshooting

- **A number does not match the anchor**: the method is wrong; fix it before going on.
