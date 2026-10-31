---
id: company
title: Fernway, the company
kind: company
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [okrs, entities, cross-cutting-rules]
---

# Fernway, the company

## Purpose

What Fernway sells, to whom, through which systems, and the words the business uses. The agent reads it first in every session, before any area or metric, so an answer never assumes a different business. It holds no metric formulas (those live in the metrics documents) and no table descriptions (those live in the catalog). RevOps owns it and updates it when the offer, the segments or a system of record change.

## What Fernway sells

- Field-service management software: scheduling, work orders and a mobile app for technicians.
- Sold as a yearly subscription with one of three plans: `starter`, `growth` and `scale`, recorded in [[silver.subscription.plan]]. Monthly recurring revenue is a twelfth of the yearly value, see [[concept:mrr]].
- There are no one-time charges, no usage-based fees and no plan changes in the data today.

## Customers and segments

- Customers are mid-size maintenance and facilities companies: electrical services, facilities management, property management, industrial maintenance, HVAC and elevator maintenance, in [[silver.company.industry]].
- They are in Germany, the United Kingdom, Australia, the United States and Canada, in [[silver.company.country]]. Every amount is in US dollars, see [[concept:cross-cutting-rules]].
- The segment, [[silver.company.segment]], follows company size in [[silver.company.employee_count]]: `smb` below 100 employees, `mid_market` from 100 to 999, `enterprise` from 1,000.
- The segment decides the team that sells to a company, see [[concept:lead-routing]].

## How Fernway sells

1. Marketing runs campaigns; a form submission can be flagged as a marketing qualified lead, see [[concept:mql]].
2. The lead is routed to an owner by segment and capacity, see [[concept:lead-routing]].
3. The owner opens a deal, which moves through qualification, discovery, proposal and negotiation to closed won or closed lost, see [[concept:funnel-stages]].
4. A won deal becomes a subscription within two weeks and gets a workspace and an onboarding kickoff, see [[concept:closed-won-provisioning]].
5. Onboarding takes the customer to go-live; Customer Success keeps and grows the account.

The typical decision maker is an operations or field-service leader (Head of Field Service, Operations Manager, COO), with a procurement lead and an IT manager involved, as in [[silver.contact.job_title]].

## Systems and sources of truth

| Topic | System | Source of truth for |
|---|---|---|
| Deals and funnel | CRM | owners, companies, contacts, deals and stage history |
| Revenue and customers | Billing | subscriptions, invoices and payments |
| Account health | Customer Success tool | health scores, tickets and onboarding milestones |
| Lead flags | Marketing forms | campaigns and form submissions |

Every system lands in the lakehouse; the agent reads only gold. When two systems disagree, the source of truth wins, see [[concept:cross-cutting-rules]].

## Glossary

- **Account**: a company in the CRM, [[silver.company]]. Not the same as a customer.
- **Customer**: a company with a paid subscription in force, see [[concept:active-customer]].
- **Deal**: one sales opportunity, [[silver.deal]]. Bookings are the yearly value of won deals; MRR comes from subscriptions.
- **MQL**: marketing qualified lead. Marketing and Sales flag it differently, see [[concept:mql]].
- **Owner**: the person responsible for a company or deal, [[silver.owner]].
- **Go-live**: the onboarding milestone when the customer uses Fernway in production, [[silver.onboarding_milestone.milestone]].
- **Health band**: green, yellow or red, from the score in [[silver.health_score.band]].
