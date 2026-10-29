---
name: handoff
description: >
  Write a session handoff and stop. Use when the user says "/handoff",
  "handoff", or the context ring is high and they want a fresh chat.
disable-model-invocation: true
---

# Handoff

Pattern from the handoff skills used on Cursor (write the state, do not resume it). Save `.handoff/<date>-<slug>.md`. That directory is gitignored.

Include:

- Goal.
- Active design mode and active plan.
- Decisions already made.
- Files touched, by path.
- What failed.
- Next step, as a note for a human, not an order to execute.
- Suggested skill to invoke next (`plan-architecture`, `development`, `orchestrator`, …).

Point at existing plans and diffs. Do not paste them. Redact tokens, passwords, and personal data.

Then stop. Do not edit code, run tests, or start the next step.
