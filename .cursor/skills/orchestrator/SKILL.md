---
name: orchestrator
description: >
  Multi-agent pipeline. A stronger model writes the implementation plan, a
  cheaper model builds one slice, a third model reviews and does not edit.
  Use when the user says "orchestrate" or "/orchestrator".
disable-model-invocation: true
---

# Orchestrator

The user assigned these models. Pass them on the Task tool. If a slug is rejected, use the next slug in that row and do not retry the rejected one.

| Role | Model | Fallback |
|---|---|---|
| Planner | `claude-opus-5-5-medium` | `claude-fable-5-1-thinking-high`, then `gpt-5.6-sol-medium` |
| Implementer | `grok-4.7-high-fast` | `cursor-grok-4.6-high`, then `gemini-4-argon-medium` |
| Controller | `claude-sonnet-5-5-high` | `gpt-5.6-sol-medium` |

Planner and implementer must be different models. Run them in order, in the foreground (`run_in_background` false). Local environment. One slice only.

## 1. Planner

`subagent_type: generalPurpose`. Prompt it to read `.cursor/skills/plan-implementation/SKILL.md` and write `.cursor/plans/impl-<slug>.md` only. Paste the user request and the data rules (EPSG, `uuid.uuid5`, null stays null, frozen `cim_wizard_integrated_2026/`, no cross-project imports). Tell it not to edit code.

## 2. Implementer

After the plan file exists, spawn a new generalPurpose agent. Paste the first unblocked slice in full. Tell it to read the design skill that slice names (default `.cursor/skills/development/SKILL.md`) and to edit only the allowed paths.

## 3. Controller

Spawn a new generalPurpose agent. Paste the slice and tell it to inspect the diff. It must not edit files. Verdict is pass or fail, with the rule or slice line that failed.

On fail, one implementer pass with that verdict, then one more controller. Then stop, even if it still fails.

## Report

Plan path, slice, implementer model, verdict. Do not rebuild the slice yourself.
