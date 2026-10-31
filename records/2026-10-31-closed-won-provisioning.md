---
date: 2026-10-31
type: automation
pr: "#41"
author: Leonardo Ippolito
---

# The closed-won provisioning automation

## What was done
Built `automations/closed-won-provisioning/provision.py` from its spec: for each closed-won deal event it decides requested, skipped or held, and writes one line per deal to `observability/logs/provisioning-<date>.md`, the simulated workspace request (ADR-0011). Added 27 tests, marked the spec built and ticked its checklist.

## Why
The rules lived in a context document and a spec, and the cases that must not be provisioned (no company, possible duplicate, already billed) were the point of the automation.

## Result or decision
- Rules are read from the context document each run: the two-week wait and the one milestone requested (kickoff). If the document stops saying them in the expected words, the run stops with an error.
- Checked in the document's order: not closed_won, no company, possible duplicate (held for a person), already has a subscription. Every skipped or held deal is listed with its reason, so nothing is dropped silently.
- A requested deal with no subscription after the wait is still requested but marked for Finance; this uses an optional `closed_won_at` date in the event.
- The deal id is the idempotency key. A second run replaces each deal's own line and adds nothing. A missing deal id, a bad date or a repeated id stops the run with exit code 1 and writes nothing. A missing snapshot does not stop it; the report says the backlog figure is unavailable.
- Two small additions to the spec's event: a `stage` field, because the spec forbids provisioning a deal that is not closed_won and the event must carry that, and the optional `closed_won_at`. The spec's Trigger line now lists them.
- It never sets a plan or price, contacts a customer or touches an existing workspace: it has no code for any of those. A test checks the source for write and send calls.
- Not proven: it has not run against the real snapshot table or any product API, which does not exist here.

## Rules and context changed
None.

## Follow-ups
The funnel-review automation.
