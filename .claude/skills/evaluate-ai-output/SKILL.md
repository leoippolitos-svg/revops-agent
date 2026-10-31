---
name: evaluate-ai-output
description: "Evaluates a batch of model outputs (drafts, summaries, qualifications) the way the reference design did: prompt frozen and tied by hash, results grouped by line of argument, input failures kept apart from model failures, review coverage reported. Use when someone asks to test a prompt, compare prompt versions, or check the quality of AI drafts or qualifications."
---

# Evaluate AI output

Method: section 11 of `docs/standards/revops-methodologies.md`. For building or changing a skill itself, use `skill-creator`.

## Steps

1. Freeze the prompt: record its hash (the spec of the automation holds it; `tools/check_prompts.py` keeps them in step). Never change the prompt during the batch.
2. Run the whole batch with the same inputs, and keep the outputs and the AI-steps log lines (tokens, cost, hash).
3. Group results by line of argument or intent, not globally. A group with n < 3 is not a conclusion.
4. Separate input failures (missing or wrong data) from model failures; never tune the prompt to compensate for bad input.
5. Report the mechanical checks (validation pass rate) apart from human review coverage; unreviewed is not approved.
6. Change one thing, rerun the batch, compare with the same grouping. Record the result with the hash of each version.

## Example

Prospecting drafts, 30 leads: validation passed 28; the two failures were leads with no evidence (input), not the prompt; the "paper to digital" argument read well, the "emergency dispatch" one was generic in four of five drafts, so that argument's sentence is rewritten, not the prompt.

## Troubleshooting

- **Scores moved but the prompt did not**: the inputs changed; compare the input sets first.
