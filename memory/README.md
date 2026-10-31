# Memory

What the agent should remember across questions that is not a business rule. Business rules live in `context/`; this folder holds three other kinds of memory, all indexed for retrieval.

| Folder | Holds | How the agent uses it |
|---|---|---|
| `decisions/` | Deliberate decisions with a date, a reason and a status (active, revised, revoked) | Treats an active decision as final and does not suggest reversing it |
| `patterns/` | Patterns found in the data, with confidence, sample size and dates | Mentions them as patterns, with their confidence; a person promotes one to a context rule |
| `benchmarks/` | Internal baselines of metrics over time | Compares a new number with the baseline and cites the period |

`query-history.json` keeps the last questions asked with the intent and model used, no personal data, for usage analysis and new eval cases.
