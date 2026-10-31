---
date: 2026-10-31
type: process
pr: "#68"
author: Leonardo Ippolito
---

# RevOps methodologies as reference and as skills

## What was done
- `docs/standards/revops-methodologies.md`: the analysis methods of the original, generalised and with every business number removed: cross-cutting principles (definition before number, anchors, method before business, ids before conclusions, two kinds of ambiguity, false zeros, mix versus process), ICP on two rulers with a stability filter, the canonical funnel and the rules that change a verdict, retention and NRR, health and deal scores, cohorts, forecast, account distribution, the business diagnosis protocol, revenue rules, evaluating model output, measuring automation impact, and BI traps.
- It is indexed for retrieval (category `conventions`), so the agent can search it.
- Four new skills apply it: `icp-analysis`, `business-health-diagnosis`, `automation-impact` (RevOps agent) and `evaluate-ai-output` (coding agent), each with a trigger test. The forecast, deal score, cohort and risk skills now name the method section they apply and the rules they were missing.

## Why
The owner considers the methodology a strong reference and asked for it both as a document and as skills.

## Result or decision
- The methods are stated as general practice; examples use Fernway or are illustrative. Retrieval stays at Hit@3 1.000 and MRR 0.893.

## Rules and context changed
None. Standard: RevOps methodologies; four skills updated, four added.

## Follow-ups
Gold models for the missing metrics, the proposal and EBR apps, the security review pipeline.
