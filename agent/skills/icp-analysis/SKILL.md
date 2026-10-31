---
name: icp-analysis
description: "Finds which customer cells to target, on two rulers at once (does it close, does it succeed after the sale), with a stability filter before any cell becomes a recommendation. Use when someone asks who the ideal customer is, which segment to prospect, whether the ICP still holds, or which accounts look like the best customers."
---

# ICP analysis

Method: section 1 of `docs/standards/revops-methodologies.md`. Rules: the `icp` context document.

## Steps

1. Read `icp`, `company` and `entities`. Fix the definition first: universe, unit (company), date that counts, exclusions.
2. Build the cells: segment × size band × industry, from gold.
3. For each cell measure both rulers: convertibility (win rate of mature cohorts) and post-sale fit (still a customer, churned MRR), always as `x% (n/N)`.
4. Apply the stability filter: at least two closed periods with n ≥ 15 and a spread of at most 20 points, periods side by side. Classify each cell as primary, stable secondary, secondary to monitor, or candidate (do not anchor).
5. Flag the trap quadrant: cells that convert well and churn.
6. State the best shallow rule ("IF segment AND industry") with its retention and n, as an instruction for SDRs.
7. Say what would change the conclusion and when to revalidate (every quarter).

## Example

"Who should we prospect?" Mid-market HVAC and electrical services are the primary cells on both rulers; enterprise converts but has too few closed cohorts to anchor; SMB under 50 employees is the anti-ICP. Fernway's history is one year, so every cell is still a candidate and the answer says so.

## Troubleshooting

- **A cell looks great on one year**: one year is not stable; show it as a candidate.
- **Penetration above 100%**: a data error in the size source, not a finding.
