---
date: 2026-10-31
type: process
pr: "#48"
author: Leonardo Ippolito
---

# README: what it controls, what it is worth, where it goes

## What was done
Added two sections to `README.md`: what the system controls and the limit that holds each part, and what it is worth, with the potential, the intended gains and where it goes next. Added them to the top navigation and linked the new analysis in the reading guide.

## Why
The owner will link the repository from a portfolio site and job applications, and few readers open any file besides the README. The README therefore has to carry the whole explanation, not point to a second page.

## Result or decision
- Everything stays in one README rather than a separate overview page, by the owner's choice.
- Each "what it controls" row names the limit that holds it and links to the spec, ADR or folder, so a claim can be checked.
- The gains are labelled as design intent, not measured results, because nothing has run against a real team or model. The CRM, billing, product and Slack connections are stated as simulated.
- Every relative link in the README was checked to exist.

## Rules and context changed
none

## Follow-ups
Bring in patterns from the owner's own experience, rewritten for the fictional company with nothing real. Turn the simulated Slack alert on behind its own decision record. Both need the owner's input first.
