---
id: proposal-rules
title: Proposal and account review rules
kind: rule
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [company, deal-discount, area-customer-success]
---

# Proposal and account review rules

## Purpose

What a generated proposal may recommend and what an account review narrative may say, so the two AI automations and the teams follow the same rules. Sales owns the proposal rules and Customer Success the review rules; the code enforces them. Prices and discounts are not here: they are in the deal and in `deal-discount`.

## Rules

- Plans by number of field technicians: starter up to 10 technicians, growth up to 50 technicians, scale above 50 technicians.
- Pain points a proposal may address: paper job sheets, manual scheduling, slow emergency dispatch, missed planned maintenance, no visibility of technician location.
- A proposal states the deal's yearly amount from the CRM as it is; it never computes a price, a discount or a saving.
- A proposal is a draft for the seller; it is never sent automatically.
- An account review narrative uses only numbers present in its data pack, never says "guaranteed", and ends with one recommended next step for the customer success manager.

## Owner and approvers

Sales owns the plans and pain points; Customer Success owns the review narrative rules. A change needs the owner of that part.
