# Skills

A skill is a folder of instructions that teaches an agent a repeatable workflow. This repo follows Anthropic's *Complete Guide to Building Skills for Claude*.

## Two audiences

| Folder | Used by | Example |
|---|---|---|
| `.claude/skills/` | The coding agent building this repo | `context-docs`, `open-pr` |
| `agent/skills/` | The RevOps agent answering business questions | `funnel-diagnosis`, `html-report` |

Never mix them.

## Folder rules

```
skill-name/
├── SKILL.md        # required, exact name
├── references/     # optional, long docs loaded only when needed
├── scripts/        # optional, executable helpers
└── assets/         # optional, templates
```

- Folder name in kebab-case, matching the `name` field.
- No `README.md` inside a skill.
- Names must not contain "claude" or "anthropic".

## Frontmatter

```yaml
---
name: funnel-diagnosis
description: Finds the bottleneck stage of the revenue funnel and explains its likely cause. Use when the user asks why conversion dropped, where the funnel leaks, or which stage to fix first.
---
```

The `description` decides when the skill loads. It must say **what it does** and **when to use it**, with phrases a user would actually type. Under 1024 characters, no `<` or `>`.

## Body

1. **Instructions**: numbered steps, each specific and checkable.
2. **Examples**: one or two realistic scenarios with the expected result.
3. **Troubleshooting**: common failures, cause, fix.

Keep `SKILL.md` focused. Move anything long to `references/` and point to it.

## A skill earns its place when

It encodes a workflow specific to this repo or this business. General knowledge the model already has (what CAC means, what a star schema is) does not need a skill.

## Testing

Every skill has a trigger test in `evals/skills/<name>.yaml`:

```yaml
should_trigger:
  - "why did conversion drop last month?"
should_not_trigger:
  - "write a SQL query for deals created today"
```

`tools/check_skills.py` validates folder and frontmatter rules and runs in CI.

## Anthropic's skill-creator is the method

The method for creating and improving skills is Anthropic's own `skill-creator`, copied unmodified into `.claude/skills/skill-creator/` under its Apache 2.0 license (see `THIRD_PARTY.md`). It is the reference: capture the intent, write test prompts, run them with and without the skill, grade and compare the results, improve, and optimise the description for triggering. Our `create-skill` skill applies this repository's rules on top of it: which folder (coding agent or RevOps agent), the trigger test in `evals/skills/`, `tools/check_skills.py`, and a pull request with a record.

## Third-party skills

A third-party skill may be copied only unmodified, under a license that allows it, pinned to a version and listed in `THIRD_PARTY.md`. It is never edited in place; repository rules go in our own skills. Otherwise, read it for ideas and write our own.
