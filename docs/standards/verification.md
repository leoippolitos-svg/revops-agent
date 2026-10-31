# Verification

**Whoever builds does not check alone.** A second agent, a script or a person tries to break the result before it is called done. This page lists the verifiers this repository has, what each one answers and, as important, what each one does not cover.

## The verifiers

| Verifier | Answers | Runs | Does not cover |
|---|---|---|---|
| Secret scan (gitleaks) | does this change add a credential? | every PR, no path filter | code security in general |
| Leak check | does this change add a real company term? | pre-commit and every PR | terms not on the private list |
| Personal-data guard (`tools/check_pii.py`) | does a tracked file hold an e-mail or phone number that is not fictional? | every PR | names, which are fictional by rule |
| Unit and security tests | guards on SQL, write controls, idempotency, refusals | every PR | behaviour with real data or a real model |
| Context, catalog, spec and card checks | do documents, specs and cards follow their standard and agree? | every PR | whether the content is right |
| Retrieval eval | does the expected document appear in the top 3? | every PR | the final answer |
| Router eval | is the intent right, on tuned and held-out questions? | every PR | questions unlike the sets |
| Profile eval (`evals/run_profiles.py`) | for each question, was the right intent picked, the right documents loaded and the right tools offered? | every PR | the answer itself: no model is called |
| AI security review | does the diff break the security rules? | PR, when switched on | see "green is not reviewed" |
| Derived-copy check | did a short copy fall behind its source? | every PR, warns | the content of the rule |
| Watchdog | did today's scheduled job run? | daily | whether it ran correctly |
| Adversarial reviewer (`.claude/agents/adversarial-reviewer.md`) | can a second agent break this analysis or change? | before asking for merge | anything it was not shown |
| Done verifier (`.claude/agents/done-verifier.md`) | is "done" true, with evidence? | before saying done | work outside the stated scope |

**Each verifier says in its own header what it does not test.** It is the cheapest habit on this list, and it stops anyone reading "eval green" as "answers checked".

## Adversarial review

One agent produces, another tries to knock it down. The reviewer gets the result and the sources, not the reasoning, and is asked for the strongest reason the result is wrong: a wrong definition, a partial month, a join that duplicates, a sample too small, a cause stated without evidence. Every objection is answered in the record or fixes the work. Use it for every analysis and for any change to authorisation, writes or rules.

## Green is not enough

- Checks passing means the checks passed. In the reference design an AI security review passed on the pull request and reported its findings only after the merge.
- **A false green is worse than no test.** An eval that only checked that its cases were well formed reported "5 of 5 green" for months. Every eval here states whether it runs the real thing; the profile eval, for example, never calls a model.

## Verifying data

| Technique | How |
|---|---|
| Anchors | three to five official numbers per area; a new analysis is reported only if it reproduces them within 2% |
| A lock in the script | the script stops and publishes nothing when an anchor moves or an id repeats |
| An independent path | the same month computed two ways; a gap is a finding |
| Parity against the approved version | run the new and the approved version on the same cut; explain every different cell |
| Reconciliation by id | a difference between sources becomes a list of records, each classified |
| A test for every rule that once went wrong | the mistake cannot come back silently |
| Open divergence, declared | what does not match and is not explained is written down with a hypothesis and an owner |
| Prompt version tied to the eval | the hash of the prompt is recorded with each run, so "B beats A" means something |

Human review is never kept in a file a script rewrites: derived output is regenerated, human notes are only appended.
