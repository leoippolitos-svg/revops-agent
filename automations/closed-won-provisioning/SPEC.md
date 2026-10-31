# Closed won provisioning, Spec

Status: built

## Problem
When a deal is signed, the customer should get a workspace and an onboarding kickoff quickly. Today that waits for someone to notice the win. The steps are the same every time, but some deals must not be provisioned (no company, possible duplicate, already billed), and doing it twice for one company is hard to undo.

## Trigger
A deal entering closed_won. Simulated in this repository by one deal event per run: deal identifier, stage, company identifier (or none), the duplicate flag of the company, whether a subscription already exists, and optionally the date of the win.

## Inputs
- The deal event itself. It is the one record-level input and arrives as the trigger, not from a table.
- `gold.data_quality_snapshot`: only the size of the closed won backlog without a subscription, to put in the report. Read-only.

## Rules
All provisioning rules are in the context document `closed-won-provisioning`: one provisioning per deal, which deals are skipped or held, where the plan comes from, which milestone is requested, and the two-week wait for a subscription. The automation does not repeat them and reads them at run time.
- The deal identifier is the idempotency key. The same event run twice gives one request, not two.
- A deal that is skipped or held is listed with the reason, so nothing is dropped silently.

## Effects
Writes one line per deal to `observability/logs/provisioning-<date>.md`: the deal, the outcome (requested, skipped or held) and the reason. For a requested deal the line is the simulated workspace request, the connector `product-provisioning` (ADR-0011). No other field and no other system is touched. Nothing is sent to the customer.

## Failure behavior
If the event is missing the deal identifier, the run stops with an error and requests nothing. If the snapshot table is missing, the run still handles the deal but says the backlog figure is unavailable. A real product call that fails would be retried a limited number of times with backoff and then reported. An error is never reported as "provisioned".

## Must never
- Write to any data source, or to the product, other than the one workspace request, and only with `--write`
- Read from silver or bronze
- Provision a deal that is not closed_won
- Provision the same deal twice
- Provision a deal with no company, or a possible duplicate without a person's confirmation
- Set the plan or the price, which come from billing
- Delete, rename or change an existing workspace
- Contact the customer
- Let the agent run it

## Dry run
Dry-run is the default: the outcome is printed and nothing is written. `--write` turns the effect on, and in this repository the effect is only the log file. Running twice for the same deal overwrites the same line.

## Security checklist
Standard: `docs/standards/security.md`, automation checklist. Ticked in the PR that built it (`provision.py`, `tests/test_closed_won_provisioning.py`).

- [x] Idempotent: running twice does not duplicate effects. Verified by a test that runs twice and finds the same file.
- [x] Retries with backoff, and a cap. Not applicable: there is no network call, the effect is a local file.
- [x] Respects rate limits of every API it calls. Not applicable: it calls no API.
- [x] Failures are logged and alerted, never swallowed. A missing deal id, a bad date or a repeated id exits with code 1 and a message; tested.
- [x] Credentials scoped to the minimum and registered. It uses none; it reads the registered `lakehouse` read-only and its simulated write is the registered `product-provisioning`.
- [x] Dry-run mode for anything that would write to an external system. Dry-run is the default and writes no file; tested.
