---
name: design-runtime
description: >
  Sketch mode. Pure functions, frozen dataclasses, and plain objects on the
  happy path, with no error handling. Use when the user says "design runtime"
  or the mode controller names design runtime.
disable-model-invocation: true
---

# Design runtime

Interactive sketch. One function, then stop and ask the next decision. Recommended answer included, so "yes" accepts it.

## Write

- Pure functions, `@dataclass(frozen=True)`, plain objects.
- Happy path only. No `try`/`except`, no validators, no custom exceptions.
- No FastAPI, no database session, no `@parallelizable`, no new dependency.
- Put it in `env_info_modeler/core_logic/`: one module or one notebook cell beside the call.
- `print` is allowed here. A notebook may show the result.

## Before writing

State assumptions in a sentence. If two readings exist, ask. Do not pick silently.

Karpathy simplicity applies here: minimum code, nothing speculative, no error handling for a case you have not seen. Touch only the lines this step needs.

## Stop

Show the function. Ask one question about the next decision. Do not build the rest of the module.
