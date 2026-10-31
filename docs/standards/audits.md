# Audits

How to build an audit that compares two sources and tells a person what to fix. Every audit in `automations/` follows this skeleton; the `new-automation` skill uses it for any audit. It comes from the reconciliations the reference design ran between contracts, the CRM and billing.

## The skeleton

1. **Source A against source B, and which one is the truth.** Name both and the source of truth for the topic (`cross-cutting-rules`). When they disagree, the truth wins and the other is corrected.
2. **A join key with measured coverage.** Match only on an explicit id (a deal id carried by the subscription), never on a name or a fuzzy similarity. Report how many records found a match and how many did not.
3. **Scope first.** Apply the scope (period, status, what is excluded) before computing anything, and print it at the top of the report.
4. **Classify every difference**, in a fixed order, so each record falls in exactly one class.
5. **Three destinations**: a **divergence** someone must fix; a **pending** item that is expected to resolve by itself (a subscription not started yet within its wait); a **known case** that is documented and accepted. Pending items that outlive their wait become divergences.
6. **The owner of each correction**, by class: the team that owns the source to be corrected.
7. **An actionable alert**: how many, the worst items by id, and the owner, built by code. No alert when nothing needs a person.
8. **A proposal, never a correction.** The audit lists what should change; a person or an authorised automation changes it.
9. **Dry run, a test round, then release.** Run read-only first, compare the result with a manual check, and only then schedule it.
10. **A kill switch** for every effect (the alert included), through the shared write controls.
11. **Never correct in bulk without approval**, item by item.

After a correction is applied, the next run is the reconciliation: the item leaves the list, or it was not fixed.

## Traps that apply to all audits

- A difference counted without its list of ids cannot be acted on, and the same mistake comes back. Always keep the ids.
- A partial period inflates "missing" items: a subscription starts up to two weeks after the win.
- A source corrected by hand is overwritten by its next import; fix it at the origin.

## Template for a new audit

Copy into the automation's `SPEC.md` and fill every line:

- **Question**: which disagreement, in one sentence.
- **Sources**: A, B and the source of truth.
- **Join key**: the explicit id, and the expected coverage.
- **Scope**: period, statuses, exclusions.
- **Classification, in order**: each class and its destination.
- **Owner of each correction**: by class.
- **Message**: the exact alert text template.
- **Where results are kept**: the report file and its retention.
- **Writes**: none, or the write-back authorization it uses.
- **Operation**: schedule, kill switch, catalog card.
- **Dated decisions**: what was decided about edge cases, with the date.

### Checklist before turning it on

- [ ] A dry run matched a manual check on a sample of ids.
- [ ] Every class has an owner and a destination.
- [ ] The alert has been read by its owner once and is actionable as written.
- [ ] The catalog card exists, and the kill switch is documented.
