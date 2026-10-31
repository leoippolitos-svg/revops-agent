# Query history

`query-history.json` keeps the last questions asked to the agent, with the intent, the skill and the model used. It feeds usage analysis and new eval cases.

- At most 200 entries; the oldest drop off.
- No personal data: the question text only, no user name or e-mail.
- Written by the agent loop when it logs an answer; never edited by hand.
