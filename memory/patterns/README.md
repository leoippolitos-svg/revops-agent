# Patterns

Patterns found in the data that are not rules yet. One file per pattern.

## Format

Front matter: `metric`, `confidence` (low, medium, high), `sample` (how many records or periods), `first_seen`, `last_checked`, `status` (candidate, confirmed, promoted, dropped). Sections: Description, Evidence, How to use it.

## Life cycle

A pattern starts as a candidate, is re-checked when new data arrives, and is promoted to a context rule only by a person, in a pull request. The agent never promotes a pattern on its own.

No pattern is recorded yet: the fictional data covers one year, which is too short for a pattern to be more than a candidate.
