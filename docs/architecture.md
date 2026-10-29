# Architecture

## Data flow

1. **Generator** writes fictional raw files for four sources: CRM, marketing forms, billing and Customer Success. It injects known data-quality issues (duplicates, broken associations, late updates) so audits have something to find.
2. **Ingestion** appends each batch to `bronze` with load metadata.
3. **dbt** builds `silver` (clean entities) and `gold` (business grain). Tests run on every build.
4. **Checks** compare today against yesterday and alert on failures or unexpected swings.
5. A scheduled job simulates "one more day" of business so the lakehouse keeps moving.

## Customer journey

Gold models follow the Bowtie: acquisition on the left (lead → MQL → SQL → opportunity), the close in the middle, recurring revenue on the right (onboarding → active → retained → expanded).

## Context layer

| Piece | Holds | Read by |
|---|---|---|
| Catalog | What each table and column is | Agent, MCP |
| Context documents | What each business concept means | Agent, MCP |
| Records | What was done, when and why | Agent |

## Agent

1. **Router** classifies intent (see `agent/directives/routing.md`) and picks a model tier.
2. **Retrieval** loads only the context the question needs.
3. **Tools** query gold read-only.
4. **Answer** states the number, the definition used, the source tables and any caveat.
5. **Fallback** handles ambiguity, missing context and out-of-scope requests (`agent/directives/fallback.md`).

## From answer to routine

An analysis answers once; a routine answers every week without being asked. Recurring questions graduate into scheduled jobs (funnel diagnosis, data audits), and the team's corrections flow back into the context layer as pull requests.
