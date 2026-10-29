---
name: plan-implementation
description: >
  Implementation plan split into slices a cheaper model can build.
  No application code. Use when the user says "plan-implementation" or
  "plan-implimentation".
disable-model-invocation: true
---

# Plan: implementation

Do not edit application code. Read the architecture note if one exists. If it does not, say so and write the plan against the current code.

## Write

Create `.cursor/plans/impl-<slug>.md`.

For each slice:

- Outcome in one sentence.
- Allowed paths. Anything else is out of bounds.
- Design mode for that slice: professional design, or development.
- Public behavior to test. One check per slice.
- Blocking slices, if any.

Keep a slice small enough for one pass: one module or one route. Prefer an existing function over a new one. No code snippets unless a prototype already settled a type or a schema; then quote only that shape.

## Stop

Show the path and the first unblocked slice. Do not implement it unless the user said orchestrate or implement.
