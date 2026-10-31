# Prompt library

Every prompt this repository sends to a model, where it lives, who uses it and what shape its answer must take. The repository is the source of truth: each prompt file's SHA-256 is recorded here or in its automation's spec, and `tools/check_prompts.py` fails CI when a prompt changes without its hash, so every result and evaluation can be tied to the exact prompt behind it. How prompts are written: [docs/standards/prompt-patterns.md](standards/prompt-patterns.md). How they are evaluated: the `evaluate-ai-output` skill.

| Prompt | Used by | Tier | Answer shape | File and hash |
|---|---|---|---|---|
| Agent identity, reading order and rules | the agent, every question (cached block 1) | fast or standard | prose answer | `agent/directives/AGENT.md`, `fallback.md`, `routing.md` |
| Intent classifier | the agent, when the classifier is on | fast | one intent id | `CLASSIFIER_PROMPT` in `agent/agent.py` |
| Retrieved-context header | the agent, block 4 | n/a | n/a | `RAG_HEADER` in `agent/agent.py` |
| Conversation title | the agent chat, first question of a thread | fast | `{"title"}`, at most 60 characters | conversation-title.md, prompt sha256: `1bacff879eeb069248d2071827023636fb0616a18a1d0c034a416e8827150673` |
| Chunk summary | retrieval ingest with `--summaries`, display only | fast | `{"summary"}`, at most 160 characters | chunk-summary.md, prompt sha256: `9dd25037a0b88190afa556e2e7811fce8e1471a0aaa216458c41b57a028b2e64` |
| Site qualification | `automations/site-qualification` | fast | fit, technicians, services, quotes, summary | in its spec |
| Prospecting drafts | `automations/prospecting-drafts` | fast | first touch, follow-up, arguments used | in its spec |
| Meeting fields extraction | `automations/proposal-generator` | fast | technicians, pain points, current tool, decision date, quotes | in its spec |
| Account review narrative | `automations/ebr-narrative` | fast | narrative, next step | in its spec |
| On-call agent | `.github/workflows/oncall.yml` | standard | the report JSON in the prompt | `oncall/prompt.md` |
| Reviewer agents | the coding agent | n/a | a verdict with evidence | `.claude/agents/` |

The two prompts above with their hash in this table live in `agent/prompts/`. Every model call made through `automations/_lib/ai_step.py` logs its prompt hash, tokens and cost in `observability/logs/ai-steps.jsonl`.
