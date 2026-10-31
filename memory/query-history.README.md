# Query history

`query-history.json` keeps the last questions asked to the agent, with the intent, the skill and the model used. It feeds usage analysis and new eval cases.

- At most 200 entries; the oldest drop off.
- No personal data: the question text only, no user name or e-mail.
- **Not written yet.** The agent log keeps no question text by design (`agent/agent.py`). Keeping questions here needs a decision on retention and on who may read them, as the original made for its chat (conversations private on screen, readable by jobs for evaluation). Until then the file stays empty.
