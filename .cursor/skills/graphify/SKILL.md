---
name: graphify
description: >
  Query a local knowledge graph of one project folder. Use when the user
  says "/graphify" or "graphify" and names a path. Do not index the whole repo.
disable-model-invocation: true
---

# Graphify

Wrapper around [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify). The CLI is `graphify` from the PyPI package `graphifyy`. This skill does not install an always-on `.cursor/rules/graphify.mdc`. That rule would load on every turn.

## Scope

Run on one project the user names (`env_info_modeler/`, `semantic/`, `cim-database/`, or a smaller folder). Refuse the repo root. This monorepo holds PDFs, CityGML, and notebooks; a full graph is the wrong default.

## Run

If `graphify` is on `PATH`:

```bash
graphify <named-folder> --no-viz
```

Read `graphify-out/GRAPH_REPORT.md` for the answer. Mark an edge `EXTRACTED` or `INFERRED` the way the report does. Do not treat an inferred edge as a fact from the source.

If the command is missing, stop and give the user:

```bash
uv tool install graphifyy
```

Do not pip-install a different package with a similar name. Do not run `graphify install --project`.
