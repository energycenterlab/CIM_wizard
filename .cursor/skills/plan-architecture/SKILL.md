---
name: plan-architecture
description: >
  Architecture plan for one CIM Wizard subproject. No application code.
  Use when the user says "plan-architecture".
disable-model-invocation: true
---

# Plan: architecture

Do not edit application code. Read `repo-map` and `project-context` before choosing a folder.

## Write

Create `.cursor/plans/arch-<slug>.md`.

1. The one folder that will own this, and the folders that stay read-only.
2. What counts as one building, which CRS is stored, which CRS is measured, and which fields stay null.
3. Two options at most, then one recommendation. Say what each option refuses to do.
4. Data flow: which existing module is called, and what it returns. No new framework.
5. Out of scope.

Look up facts in the repo. Ask the user only for a decision. One round of questions, each with a recommended answer, then wait.

## Stop

Show the path. Implementation waits for `plan-implementation` or an explicit implement request.
