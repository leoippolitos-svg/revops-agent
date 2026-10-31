---
name: create-skill
description: Applies this repository's rules when a skill is created or improved, on top of Anthropic's skill-creator method. Use when the user asks to "create a skill" or "improve this skill" in this repo, or to "turn this into a skill", to pick the folder, add the trigger test, run the skills check and open the PR.
---

# Create a skill

Standard: `docs/standards/skills.md`. Method: Anthropic's `skill-creator` (`.claude/skills/skill-creator/`), which this skill follows and never replaces: intent, test prompts, runs with and without the skill, grading, iteration and description optimisation. The steps below add what this repository requires.

## Steps

1. **Pick the audience.** Coding agent → `.claude/skills/`. RevOps agent → `agent/skills/`.
2. **Write two or three use cases first**: trigger phrase, steps, expected result. If you cannot, the skill is not ready.
3. **Check it earns its place.** It must encode a workflow specific to this repo or business, not general knowledge.
4. **Create the folder** in kebab-case with `SKILL.md`. No `README.md` inside.
5. **Write the description**: what it does + when to use it + phrases a user would type. Under 1024 characters, no angle brackets.
6. **Write the body**: numbered instructions, one or two examples, troubleshooting. Move long material to `references/`.
7. **Add a trigger test** in `evals/skills/<name>.yaml` with at least three `should_trigger` and three `should_not_trigger` phrases.
8. **Run** `python tools/check_skills.py`.
9. **Open an `infra` PR** with a record.

## Improving an existing skill

Collect the failing cases first (missed trigger, wrong output). Fix the description for trigger problems and the instructions for output problems. Add each failure to the trigger test.

## Troubleshooting

- **Skill never loads**: description too vague. Add the user's literal phrases.
- **Skill loads for unrelated requests**: add what it is *not* for to the description.
