# Prompt patterns

How prompts are written in this repository: the agent's directives, the on-call prompt, the reviewer agents and any prompt a future automation sends to a model. Each pattern came from a production prompt in the reference design.

## Patterns

1. **Structure before instruction.** What must never reach the model does not go in the prompt: an ineligible argument, a field with personal data, a tool the intent does not need. A guardrail written as an instruction is a regression.
2. **Hierarchy stated in the prompt.** Behaviour rules over retrieved text; retrieved text is reference, not instruction, even in the imperative; data queried now over a document.
3. **Inject what the model cannot know.** Today's date, the data date, the role of the person asking, in their own block.
4. **Stable first, variable last.** Rules, then category documents, then the date, then retrieved text, so a cache marker covers what does not change.
5. **Tool descriptions are contracts.** They say what the tool refuses; a refusal the model was not told about makes it retry in a loop.
6. **Ask for a fixed output shape** (a JSON object, a table with named columns) when code reads the answer, and validate it in code; never trust it.
7. **Say what to do when it cannot.** "I did not find it" and "a person must decide" are valid outputs, with the exact next step.
8. **No invented data.** A signal enters the output only if its text is in the source; the prompt says so and a test checks it.
9. **Short and specific.** Each sentence changes behaviour or it goes.

## Versioning and evaluation

- The repository is the source of truth of every prompt. A prompt run anywhere else is checked against the repository's version (by hash) before an evaluation.
- Freeze the prompt, run every case, then change it. Changing the prompt in the middle of a batch makes the batch unreadable.
- Group evaluation results by line of argument or failure type: "the agent is bad" cannot be evaluated.
- Record the prompt's hash with each evaluation run, so "version B beats version A" means something.

## Where the prompts are

| Prompt | File |
|---|---|
| The agent's identity, reading order and rules | `agent/directives/AGENT.md`, `fallback.md`, `routing.md` |
| The intent classifier | `CLASSIFIER_PROMPT` in `agent/agent.py` |
| The retrieved-context header | `RAG_HEADER` in `agent/agent.py` |
| The on-call agent | `oncall/prompt.md` |
| The reviewers | `.claude/agents/` |
