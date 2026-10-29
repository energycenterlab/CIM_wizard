---
name: plan-literature-review
description: >
  Literature plan. Collect sources and write a note. No application code.
  Use when the user says "plan-literature", "plan-litrature", or
  "literature review".
disable-model-invocation: true
---

# Plan: literature review

Do not edit application code, notebooks, or schemas.

## Write

Create `.cursor/plans/lit-<slug>.md` as an Obsidian note. Read `.cursor/skills/obsidian-markdown/SKILL.md` first.

Frontmatter: `title`, `date`, `tags` (`literature`, plus the topic), `status: draft`.

Sections:

1. Question this note answers.
2. Sources. Author, year, title, and where the file or URL sits in this repo. If you cannot open it, say so. Do not invent a citation, page, or number.
3. What each source actually says, in a few lines, with the claim separated from your reading.
4. What this repo already does (`paper2/`, `env_info_modeler/`, `semantic/`). Link with wikilinks to notes that exist, and with normal links to files.
5. Open questions. One recommended next source or next note.

## Stop

Show the path. Do not start architecture or implementation.
