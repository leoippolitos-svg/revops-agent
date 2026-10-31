---
date: 2026-10-31
type: context
pr: "#49"
author: Leonardo Ippolito
---

# Context: the company, each area, metrics, the CRM map and cross-area rules

## What was done
Added 25 context documents beyond the concepts, in folders by kind: the company, its OKRs and its teams and people (`company/`); one document per area for Marketing, SDR, Sales, Enterprise, Onboarding, Customer Success and RevOps (`areas/`); the metrics of each area plus product usage (`metrics/`); the CRM map and the data map of gold (`crm/`); the revenue snapshot report and external benchmarks (`reports/`); and the ICP, the write-back rules and the app inventory (`rules/`). `tools/check_context.py` now checks every kind with its own required sections, a `[[doc:id]]` annotation and a code-block rule; five tests cover it. The context standard explains the kinds.

## Why
The owner's original agent organised its knowledge by area: company, OKRs, entities, one directive per area, metrics per area, CRM maps, reports and write-back rules, read in a fixed order. This repository only had seven concepts in one folder, so the agent had no way to know who is who, what each area measures or how the CRM is laid out. The concepts stay; the new documents point at them instead of repeating them.

## Result or decision
- Every document opens with **Purpose** (what it is for, who reads it, what does not belong, owner), the pattern of the original skeletons.
- A metric with no gold source is listed as "not in gold yet" (cost per MQL, time to go-live, health band, speed to lead). That is honest about the data and gives the next data tasks.
- Only the CRM and data maps may hold a SQL block, for the model query the agent starts from: in the original, telling the agent which table to query and showing one working query was the biggest quality gain.
- OKR targets and benchmarks are fictional. Benchmarks stay draft with placeholder values until sourced, and the document tells the agent to say so.
- Not done here: retrieval and the MCP server still read only the concepts. They learn the new documents in the retrieval and prompt pull requests that follow.

## Rules and context changed
New documents listed above; `context/index.yaml` gained a `documents` list; `docs/standards/context-documents.md` gained "Kinds of documents". No existing concept changed.

## Follow-ups
Agent reading order and security policy, session closing, memory and the projects workspace come next, then the app template, then the agent mechanisms.
