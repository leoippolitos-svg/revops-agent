---
id: prospecting
title: Site qualification and prospecting messages
kind: rule
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [icp, area-sdr, company]
---

# Site qualification and prospecting messages

## Purpose

What the site qualification may conclude about a company and which arguments a prospecting draft may use, so the AI steps and the SDRs follow the same rules. The two AI automations read it at run time, and every guardrail below is enforced in code, not only in the prompt. The ICP itself is in its own document. Sales owns it with Marketing; a new argument needs approval from both.

## Rules

- Service labels the qualification may use: HVAC maintenance, electrical services, elevator maintenance, industrial maintenance, facilities management, property management, refrigeration.
- A qualification quote must appear word for word in the website text; a quote that does not is dropped and the result goes to review.
- Contact details (e-mail addresses, phone numbers) are removed from the website text before it reaches the model.
- Eligible arguments, each with the evidence it needs:
  - `arg-paper-to-digital`: Replace paper job sheets with digital work orders your technicians fill in on their phones. Needs: evidence mentioning paper.
  - `arg-scheduling-scale`: Schedule hundreds of jobs a month without spreadsheets, with technicians assigned by skill and location. Needs: technicians mentioned.
  - `arg-emergency-dispatch`: Dispatch the nearest available technician to an emergency call-out in minutes. Needs: evidence mentioning emergency.
  - `arg-planned-maintenance`: Turn planned maintenance contracts into recurring jobs that schedule themselves. Needs: evidence mentioning planned maintenance.
- A draft uses only eligible arguments whose evidence was found. A company with weak or unknown fit gets no draft.
- A draft never mentions prices, discounts, guarantees or competitors, never holds a link, and never holds a number that is not in its input.
- A draft is at most 600 characters for the first touch and 400 for the follow-up. The SDR reviews and sends it; nothing is sent automatically.

## Owner and approvers

Sales owns the arguments with Marketing; a new argument or a change to the forbidden claims needs both.
