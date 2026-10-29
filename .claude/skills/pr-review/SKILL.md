---
name: pr-review
description: Reviews a pull request with evidence-backed findings and a clear verdict. Use when the user asks to "review this PR", "check my changes", before merging any PR, or after open-pr finishes.
---

# Review a pull request

## Steps

1. **Read the PR**: description, type, diff, record. Separate core files from mechanical ones (lockfiles, generated files).
2. **Run the deterministic checks first** (CI scripts, tests, `python tools/check_skills.py`). Anything they catch is not repeated in the review.
3. **Review passes** on core files:
   - Correctness: do the numbers and logic do what the record claims?
   - Context: does every changed rule match an updated context document? Does any SQL contradict a canonical definition?
   - Security: secrets, write access, unvalidated input (see `docs/standards/security.md`).
   - Structure: naming and layers per `docs/standards/data-modeling.md`.
   - Filler: comments that restate the code, dead code, unexplained magic numbers.
4. **Verify every finding.** Re-read the cited code. Internal claims need `file:line`; external claims need an official URL. Drop anything without evidence.
5. **Assign severity**: blocker, should-fix, nit (max five nits).
6. **Verdict**: any blocker → request changes. Only nits or nothing → approve. Otherwise → comment.
7. **Post one consolidated review** with `gh pr review`.

## Re-reviews

Check only whether earlier findings were resolved and whether new blockers appeared. Stop after three rounds and escalate to the owner.

## Troubleshooting

- **Cannot approve your own PR on GitHub**: post as a comment with the verdict in the first line.
