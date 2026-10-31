---
id: icp
title: Ideal customer profile
kind: rule
owner_team: Marketing
status: draft
last_reviewed: 2026-10-31
related: [company, area-marketing, area-sales]
---

# Ideal customer profile

## Purpose

Which companies Fernway should go after first, and which signals say a company will not succeed after the sale. Marketing and SDRs read it to build target lists; the agent reads it when asked "who should we target" or "is this company a fit". It holds criteria, not lists of companies. Marketing owns it with Sales and RevOps; it is validated every quarter against won and churned customers, and stays draft until the first validation has enough customers.

## Rules

- **Fit**: industries where field technicians are the core of the business: HVAC, electrical services, elevator maintenance, industrial maintenance, facilities and property management, in [[silver.company.industry]].
- **Size**: `mid_market` first (100 to 999 employees), then `smb` above 50 employees, then `enterprise` through the enterprise team only, from [[silver.company.segment]] and [[silver.company.employee_count]].
- **Countries**: the five where Fernway sells: DE, UK, AU, US and CA.
- **Buyer**: an operations or field-service leader is involved; a deal with only an IT contact is a weaker fit.
- **Anti-profile**: companies under 20 employees, or with no field technicians. Leads from them are not routed until a person confirms the fit.
- **Validation**: every quarter, compare won and churned customers by industry and size. A cell with fewer than 10 customers is not used to change the profile.

## Owner and approvers

Marketing owns the profile; a change needs Sales and RevOps approval in the pull request. The quarterly validation is an analysis pull request with its own record.
