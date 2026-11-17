---
date: 2026-11-17
type: app
pr: "#75"
author: Leonardo Ippolito
---

# The agent chat looks like the rest of the project

## What was done
- The agent chat page has a new look in the same style as the social preview image. It is dark by default and has a light palette for people who ask for one.
- Each answer now has:
  - a row of pills with the intent, tier, tools called and which step of the cascade decided;
  - the demo label set apart from the answer, so it is not mistaken for part of it;
  - the suggested next question in the accent colour.
- The rows of a query are drawn as a real table. Before, every value was squeezed into one sentence. The scripted model keeps those rows apart, and the server sends them as `table`. A real model writes the rows into its own answer, so in that mode `table` is null.
- The screenshot in the README was taken again: `docs/img/agent-chat.png` replaces the old jpg.
- 1 test added: query rows go to the table, and a search result draws no table.

## Why
The owner wanted the README images to look as good as the social preview. The old answer also showed raw values in one line, which was hard to read.

## Result or decision
- Nothing changed in the agent: the router, prompt blocks, tools and budget are the same.
- The page still builds every element with textContent, and the Content-Security-Policy is unchanged.

## Rules and context changed
None.

## Follow-ups
None.
