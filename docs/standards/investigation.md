# Investigation

How a person or an agent diagnoses a number that does not match, or an incident, without guessing. The `data-discrepancy` and `funnel-diagnosis` skills follow it.

## The protocol

| # | Step | Required output | The mistake it prevents |
|---|---|---|---|
| 1 | **Fix the symptom** | the observed number, the expected one, the gap, the source of each, the window | investigating "it looks odd" |
| 2 | **Collect the context** | the context document that says how it should be; recent changes (documents, models, jobs, deploys) | ignoring that something changed yesterday |
| 3 | **List hypotheses, ordered** | three to six, most likely first, **written before querying** | anchoring on the first explanation |
| 4 | **Eliminate with real queries** | for each hypothesis: the query, the result, the verdict | "probably X" with no tool call |
| 5 | **Isolate and reproduce** | the smallest case that shows it: one id, one month, one row | a symptom taken for the cause |
| 6 | **Prove with a list of ids** | the records that make the gap, each classified | an aggregate that lies |
| 7 | **Record** | the root cause in a context document if stable; the digest in the project; a decision record if a decision changed | the next session redoing the investigation |

Rules while investigating:

- **Read-only.** An investigation never writes to the system it investigates, not even "to test".
- **The real schema wins** over the documented one; a difference is a finding to record.
- **Never fill a gap with an unsigned estimate.** "I did not find it" is a valid answer.
- **Suspect the method before the business.** A number that contradicts what people know is almost always a join, a filter, a duplicate or a window.
- **"Decision taken: none"** is a legitimate result. Diagnosis and fix are separate steps; the fix starts with a spec.

## Hypotheses worth testing first

| Family | Hypothesis | Quick test |
|---|---|---|
| Duplication | a change log keeps several versions per record | count rows per key; take the latest version **before** the join |
| Duplication | a many-to-many join multiplies rows | count before and after the join |
| Filter | a forgotten scope (segment, customer type) | redo with the scope of the context document |
| Filter | a label that does not exist in the data (a "false zero") | list the distinct values of the field |
| Window | a calendar year against a sales cycle; a partial period against a closed one | redo on a symmetric window |
| Key | the wrong join key; spaces or case in the key | sample ten keys on both sides |
| Sentinel | empty dates stored as 1900 or 1970; a left join turning a missing number into 0 | the minimum date; null instead of zero |
| Status | a current status rewriting the past | the same computation with the status on the event date |
| Source | two systems out of sync; a snapshot against live data | when each source was last updated |
| Code | what runs in production is not what is in the repository | read the deployed version before analysing code |
| Mix | the average moved because the composition moved | split the change into mix and rate |

## Using agents in an investigation

Fan out the read-only work: one subagent per hypothesis, each returning the query, the result and a verdict. The main session keeps the hypothesis list and decides. The `adversarial-reviewer` then tries to break the conclusion before it is reported.
