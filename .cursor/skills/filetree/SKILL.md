---
name: filetree
description: >
  Refresh a one-line map of the top-level projects. Use when the user says
  "/filetree" or "filetree".
disable-model-invocation: true
---

# Filetree

Idea from [nekocode/filetree-skill](https://github.com/nekocode/filetree-skill) (MIT): one line per area, what it is for, not how it is built. This repo is too large for a hash of every file, so the map stays at the top level.

When named, rewrite `FILETREE.md` at the repo root.

- Section `Core`: `.cursorrules`, `.cursor/rules/mode-controller.mdc`, `.cursor/rules/repo-map.mdc`, `.cursor/rules/project-context.mdc`.
- Section `Projects`: each existing top-level directory. One line, under 25 words, present tense, the role from `repo-map` if that rule already states it.
- Skip hidden directories, `output/`, data blobs, and anything under a project.

Do not describe a file you did not list. If a directory is missing, omit it.
