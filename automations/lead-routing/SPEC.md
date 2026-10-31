# Lead routing, Spec

Status: built

## Problem
A new marketing qualified lead waits until someone decides who takes it. The decision is the same every time (segment, then capacity), but it is made by hand, so some owners are overloaded and some leads wait. The automation applies the rule the moment a lead is flagged.

## Trigger
A new lead event: a form submission that Marketing flagged. Simulated in this repository by one lead record per run (company, segment, current company owner if any).

## Inputs
- The lead event itself: company, segment, current owner of the company. It is the one record-level input, and it arrives as the trigger, not from a table.
- `gold.owner_workload`: team and open deals per owner, read-only.

## Rules
All routing rules are in the context document `lead-routing`: segment to team, account continuity first, then fewest open deals, the capacity limits, and what happens when everyone is full. The automation does not repeat them and reads them at run time.
- A batch adds each assignment to the owner's open deals as it goes, so two leads never see the same count.
- The same lead event, run twice, gives the same owner and writes one assignment, not two.

## Effects
Writes one line per lead to `observability/logs/lead-routing-<date>.md`: the lead, the owner chosen, the previous owner, and the rule that decided it. This is the simulated CRM write, the connector `crm-owner-assignment` (ADR-0010). Leads that cannot be routed are listed in the same file with the reason. No other field and no other system is touched.

## Failure behavior
If `gold.owner_workload` is missing or empty, the run stops with an error and assigns nothing. A lead with no segment is not routed and is listed. When every owner of the team is at the limit the lead is not assigned and the shortage is reported, never silently given to an overloaded owner. An error is never reported as "all routed".

## Must never
- Write to any data source other than the single owner assignment, and only with `--write`
- Read from silver or bronze
- Assign a lead to a team other than the one the segment picks
- Assign a lead to an owner at the capacity limit
- Delete, merge or edit any other field of a lead or company
- Let the agent run it or change who owns a lead

## Dry run
Dry-run is the default: the assignments are printed and nothing is written. `--write` turns the effect on, and in this repository the effect is only the log file. Running twice for the same lead overwrites the same line.

## Security checklist
Standard: `docs/standards/security.md`, automation checklist. Ticked in the PR that built it (`route.py`, `tests/test_lead_routing.py`).

- [x] Idempotent: running twice does not duplicate effects. Verified by a test that runs twice and finds the same file.
- [x] Retries with backoff, and a cap. Not applicable: there is no network call, the effect is a local file.
- [x] Respects rate limits of every API it calls. Not applicable: it calls no API.
- [x] Failures are logged and alerted, never swallowed. A missing or empty table, a bad event or a repeated lead id exits with code 1 and a message; tested.
- [x] Credentials scoped to the minimum and registered. It uses none; it reads the registered `lakehouse` read-only and its simulated write is the registered `crm-owner-assignment`.
- [x] Dry-run mode for anything that would write to an external system. Dry-run is the default and writes no file; tested.
