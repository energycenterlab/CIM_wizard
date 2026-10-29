---
name: grill-me
description: >
  Relentless interview to sharpen a plan or design. Writes no code.
  Use when the user says "grill me" or "/grill-me".
disable-model-invocation: true
---

# Grill me

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `grill-me` and `grilling` (MIT). Cursor has no Skill tool, so the interview is here.

Interview until you reach a shared understanding. Map a design tree: every decision branches into the decisions that hang off it.

Work in rounds. The frontier is every decision whose prerequisites are already settled. Ask the whole frontier in one round: number each question and give a recommended answer. Word it so "yes" accepts the recommendation. Wait for the answers before the next round.

```
Q1. <title>: <question>
Recommended: <answer>

Q2. <title>: <question>
Recommended: <answer>
```

A question that depends on another question still open in this round waits for a later round.

Look up facts in the repo yourself. Decisions stay with the user.

Stop when the frontier is empty. Do not write code or a plan file until the user says the understanding is shared.
