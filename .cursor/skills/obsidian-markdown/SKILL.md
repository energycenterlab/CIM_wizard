---
name: obsidian-markdown
description: >
  Obsidian Flavored Markdown for literature notes: wikilinks, callouts,
  properties, highlights. Use when plan-literature-review writes a note,
  or the user mentions Obsidian, wikilinks, or callouts.
disable-model-invocation: true
---

# Obsidian markdown

Syntax from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) `obsidian-markdown`, trimmed to what a literature note needs. Detailed property tables stay upstream.

Use this for `.cursor/plans/lit-*.md`. Standard Markdown is assumed.

- Properties in frontmatter: `title`, `date`, `tags`, `aliases`, `status`.
- Wikilink: `[[Note Name]]`, `[[Note Name|label]]`, `[[Note Name#Heading]]`.
- Embed: `![[Note Name]]`, `![[figure.png|600]]`.
- Callout: `> [!note]`, `> [!warning] Title`. Types include `note`, `tip`, `warning`, `quote`, `question`.
- Highlight: `==text==`.
- Comment hidden in reading view: `%%text%%`.
- External URLs stay normal Markdown links. Wikilinks are for notes in this repo.

Do not invent a linked note that does not exist. A missing note is named in the open-questions section instead.
