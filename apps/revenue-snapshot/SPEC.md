# Revenue snapshot, Spec

Status: specified, not built

## Problem
Leaders ask the same four questions every Monday: how is recurring revenue moving, how many customers do we have, how much entered the funnel, and how many leads Marketing handed over. Today each answer comes from a different report with a different definition. This app shows all four on one page, each with the definition it uses.

## Users
- Sales, Marketing and Customer Success leads, who read the page.
- RevOps, who owns it and the definitions behind it.
Nobody edits data through it.

## Screens
One page, read-only.

1. **Header**: the data date (the newest export loaded) and a note that the month in progress is partial.
2. **MRR**: ending MRR by month, with new and churned MRR for the latest full month.
3. **Customers**: active customers and active subscriptions by month, shown as two separate lines.
4. **Funnel**: deals that entered each stage in the latest full month, in stage order.
5. **MQLs**: Marketing's count by month. Sales' count is shown only as "Sales agrees", never added.
6. **Definitions**: under each block, the one-sentence definition and a link to its context document.

## Data read
Gold tables only, through a read-only connection:

- `gold.mrr_monthly`
- `gold.active_customer_monthly`
- `gold.funnel_stage_monthly`
- `gold.mql_monthly`

Definitions come from the context documents `mrr`, `active-customer`, `funnel-stages` and `mql`.

## Must never
- Write to any data source
- Read from silver or bronze
- Expose a key, a token or a database path in the client
- Show a partial month as if it were a full one
- Add or average Marketing's and Sales' MQL counts
- Accept free text or SQL from the user: the page has no inputs

## Failure behavior
If gold is missing or the data date is older than two days, the page says so at the top and still shows the last data it has. An empty table shows "no data for this period", never zero.

## Design
Colors, type and spacing come from `design-system/tokens.json`. The page reads on a phone and prints on one sheet.

## Security checklist
Standard: `docs/standards/security.md`. Nothing is ticked, because nothing is built. Each item is ticked in the PR that builds the app, with how it was verified.

- [ ] No secret in client code or in the repository
- [ ] Reads data only through gold, read-only
- [ ] All inputs validated on the server side
- [ ] No raw SQL built from user input; parameters only
- [ ] Errors logged without leaking internal details to the user
- [ ] Dependencies pinned
- [ ] Spec and security review committed with the PR
