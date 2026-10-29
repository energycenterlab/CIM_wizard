---
name: development
description: >
  Put an already designed function on the framework that subproject already
  uses. Use when the user says "development".
disable-model-invocation: true
---

# Development

The function already exists from design runtime or professional design. This mode puts it on a boundary. It does not reimplement the logic in the route.

## Where

- `env_info_modeler/`: follow `cim-development-structure`. `core/` stays stateless and free of I/O. `app/` calls core. Notebooks only call. Settings stay in `config/`.
- `datalake/`: the existing Streamlit + FastAPI split. A route calls the designed function.
- `cim_wizard_integrated_2026/`: frozen. Do not add the new API there.

## Boundary

- FastAPI (or the framework already in that folder) only at the edge.
- Pydantic on the request and response. Exceptions become HTTP errors at that edge, not inside `core/`.
- No new layer, client, or dependency the folder does not already use.

## Check

State the success check before editing (a test, or one request and its response). Run it. The diff should trace to the plan slice or the user request.
