---
name: professional-design
description: >
  Harden a sketch with real branches, types, and one test per branch. No
  framework. Use when the user says "professional design".
disable-model-invocation: true
---

# Professional design

Same functions as the sketch, thickened. Still no FastAPI, no dependency injection, no repository layer.

## Add

- A branch only for a case that showed up in the data or that the user named.
- Types on every parameter and return.
- Named steps a breakpoint can sit between.
- One small test per branch. Write the failing test, then the branch, then run it.
- Null stays null. Do not invent a value the source did not publish.

## Leave out

- Error handling for impossible cases.
- A branch "for later".
- Framework code, config systems, and new abstractions used once.

## Check

Run the new tests. Report the command and the result. If a test fails, fix that branch and run again before the next branch.
