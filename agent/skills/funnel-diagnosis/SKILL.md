---
name: funnel-diagnosis
description: Finds the bottleneck stage of the revenue funnel and explains its likely cause. Use when someone asks why conversion dropped, where the funnel is leaking, which stage to fix first, or for the weekly funnel review.
---

# Funnel diagnosis

Based on the Theory of Constraints: there is always one stage that limits the whole funnel. Find it before suggesting fixes.

## Steps

1. Read `funnel-stages` and every stage definition it links to.
2. For each stage, for the period asked and the previous comparable period, get from gold:
   - volume entering the stage,
   - conversion to the next stage,
   - median time in stage,
   - top loss reason, if recorded.
3. Find the constraint: the stage with the largest drop in conversion or the largest growth in time in stage, weighted by volume.
4. Before blaming the business, rule out data causes: definition changes (records), freshness failures, known data-quality issues.
5. Check `search_records` for earlier diagnoses of the same stage.
6. Answer with:
   - the constraint stage and the evidence,
   - the most likely cause and how confident you are,
   - what would confirm it,
   - the owner team of that stage.

## Example

Question: "Why did new revenue drop in September?"
Finding: volume and win rate held; opportunity-to-proposal time doubled for Enterprise. A record from August shows a new legal review step. Constraint: proposal stage, Enterprise. Owner: Enterprise sales.

## Troubleshooting

- **Every stage looks worse**: suspect data or a definition change before the business.
- **Very small volumes**: say the sample is too small to call a constraint.
