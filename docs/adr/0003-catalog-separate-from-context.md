# ADR-0003: Catalog separate from context documents

- Status: accepted
- Date: 2026-10-29

## Context
In the original agent, per-team folders mixed column descriptions with business rules. Rules got repeated and drifted apart.

## Decision
Tables and columns are described in the catalog (dbt `schema.yml`). Business concepts are described in context documents, one concept per document, with annotations pointing to catalog entries. CI validates annotations.

## Alternatives considered
- **One document per table with rules inside**: simple, but a rule that spans five tables gets written five times.

## Consequences
Each fact has one home. Writers need to learn which home is which.
