---
date: 2026-10-29
type: data
pr: "#3"
author: Leonardo Ippolito
---

# Generator part 1: base entities

## What was done
Added `generator/generate.py`, which writes fictional CSV files for owners, companies, contacts (CRM) and campaigns (marketing) into `data/raw/`, plus `tests/test_generator.py` with 10 tests and usage notes in `generator/README.md`.

## Why
Phase 1 needs raw data before any pipeline layer can be built or tested. This part covers the stable entities; deals, billing, Customer Success and the deliberate data-quality issues come in part 2.

## Result or decision
- The generator only writes files. The bronze layer stays written by ingestion alone (`CLAUDE.md`).
- Output is fully determined by `--seed`: same seed, byte-identical files, which the tests check with a folder hash. The simulated start date is fixed (2025-01-01) for the same reason.
- No `faker` dependency: names come from short word lists, e-mails use the reserved `example.com`, and there are no phone numbers or tax IDs (`docs/standards/security.md`).
- Size: 20 owners, 300 companies, 1,000 contacts and 12 campaigns, generated in well under a second.
- Tests cover determinism, row counts, unique keys, references between files, segment versus headcount, contact dates and e-mail domains. The leak check was also run over a generated batch (0 hits).
- Company names are unique on purpose in this part; duplicates will be injected in part 2 so they can be tracked.

## Rules and context changed
none

## Follow-ups
Part 2: deals and stage history, billing, Customer Success, the data-quality issues and `--days`. CI does not run pytest yet; add it together with the first pipeline tests.
