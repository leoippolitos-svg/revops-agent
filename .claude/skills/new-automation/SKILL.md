---
name: new-automation
description: Builds an automation such as lead routing, closed-won provisioning or a weekly audit, spec first, under the automation security checklist. Use when the user asks for an "automation", "workflow", "routing rule", "alert", "scheduled check" or something that should run without a person.
---

# New automation

Standards: `docs/standards/pull-requests.md` (spec-driven flow) and the automation checklist in `docs/standards/security.md`.

## Steps


An audit (two sources compared) follows `docs/standards/audits.md`: explicit-id join, three destinations, an owner per class, a proposal and never a correction.
1. **Research**: who benefits, what triggers it, what it changes, and which team owns the outcome. Write it down.
2. **Spec**: create `automations/<name>/SPEC.md` with these sections: Trigger, Inputs (gold tables only), Rules, Effects, Failure behavior, Must never. Commit the spec before any code.
3. **Context**: every business rule the automation applies (segments, capacity, thresholds) lives in `context/`, not in code. Load `context-docs` and update it.
4. **Connectors**: list every system touched. Register each in `connectors/registry.yaml` with the `add-connector` skill. Any write needs an ADR.
5. **Implement** the smallest version. Dry-run is the default; a flag turns real effects on. In this repo effects go to a simulated destination or to `observability/`.
6. **Test**: the main path, a second run on the same input (must not duplicate effects), a failing dependency, and empty input.
7. **Checklist**: tick every item of the automation checklist and paste it in the PR.
8. Open the PR with `open-pr`, type `automation`.

## Example

"Alert when a company is flagged as a duplicate." Spec: trigger weekly, input the duplicate flag exposed through gold, effect one message in `observability/`, must never delete or merge records. A second run on the same week writes no second message.

## Troubleshooting

- **The rule keeps changing**: it belongs in a context document, read at run time, not in code.
- **No way to test an effect**: the effect is not isolated enough. Put it behind one function that dry-run replaces.
- **It needs write access to the source**: stop and write the ADR first.

## Never

- Write to a source system without an ADR and a dry-run mode.
- Swallow an error. Log it and raise the alert.
