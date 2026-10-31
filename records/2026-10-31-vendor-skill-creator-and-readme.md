---
date: 2026-10-31
type: process
pr: "#66"
author: Leonardo Ippolito
---

# Anthropic's skill-creator as the method for skills, and a README in the usual order

## What was done
- Copied Anthropic's `skill-creator` skill, unmodified, from the public `anthropics/skills` repository at commit `ca45fc4`, into `.claude/skills/skill-creator/`, with its Apache 2.0 license file. `THIRD_PARTY.md` lists source, version, license and the rules for third-party material. A trigger test was added for it.
- The rule in `CLAUDE.md` now allows a third-party copy only unmodified, under a license that allows it, pinned and listed; the skills standard names `skill-creator` as the method, and our `create-skill` now applies the repository's rules on top of it.
- Reorganised the README in the order well-rated READMEs use: title, badges, a quick start with the chat screenshot and three commands at the top, then what it is, why, status, what it controls, proof, reading guide, how it works, run it, decisions. The long tables (capabilities, folder tree, decisions) are folded in expandable blocks; the "what it never does" line stays visible.
- Removed prints that were not relevant: the revenue-snapshot screenshot (old data) and the long plan JSON, which the chat screenshot already shows.

## Why
The owner considers Anthropic's skill-creation method the reference for building skills and wanted it in the repository, not only referenced. The README was complete but put the demo and the quick start more than 300 lines down.

## Result or decision
- The copy is unmodified and its license is kept; any repository rule lives in our own `create-skill`. Updating it means replacing the folder with a newer pinned commit.
- No README content was dropped except the two prints.

## Rules and context changed
`CLAUDE.md` (third-party rule), `docs/standards/skills.md`.

## Follow-ups
None.
