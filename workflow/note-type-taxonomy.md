---
title: Note Type Taxonomy
tags: [workflow, zettelkasten, templates]
created: 2026-04-23
updated: 2026-04-28
status: active
type: workflow
scope: vault
---
# Note Type Taxonomy

This vault uses seven note types with dedicated templates. Each type has a defined scope, a home folder, and a set of mandatory frontmatter fields.

## Types

| type | folder | scope | purpose |
|------|--------|-------|---------|
| `project-index` | `permanent/` | project | Entry point for one project. One note per project. |
| `concept` | `permanent/` | domain | Project-agnostic domain knowledge (e.g. immune boosting, Bayesian inference). Survives project archival. |
| `technical` | `permanent/` | project | Non-obvious architecture, fragilities, design decisions derivable only from reading the code carefully. |
| `decision` | `permanent/` | project | Architectural or methodological choices: context, alternatives, rationale, outcome. |
| `literature` | `references/` | domain | One note per paper. Claim, mechanism, relevance, project appearances. |
| `workflow` | `workflow/` | vault | Conventions and decisions about the note-taking system itself. |
| `fleeting` | `fleeting/` | any | Low-friction dump for TODOs, ideas, open questions. Promoted to a permanent type, archived, or deleted within ~14 days. |

Session logs (`type: session-log`) live in `logs/` and are not considered permanent notes.

### Fleeting notes — relaxed rules

`fleeting` is the only type exempt from the standard requirements. The point is to capture an idea before it evaporates, so:

- **Frontmatter is minimal** — only `title`, `type: fleeting`, `created` are required (no `tags`, `updated`, or `status`).
- **No wikilink minimum** — a fleeting note may have zero wikilinks.
- **No `file:line` citation requirement** — even when topically technical.
- **Atomicity still applies** — one idea per file. Easier to promote, archive, or delete cleanly.
- **Lifecycle:** promote to `permanent/` (rewrite frontmatter to the destination type), move to `fleeting/archive/` (kept as a record of an idea you decided not to pursue), or delete. Default retirement age **14 days** — surfaced by `/save` and `/resume` (see project [[CLAUDE]]).

## Mandatory frontmatter fields

All notes:
```yaml
title, tags, created, updated, status, type
```

Additionally:
- `project:` — required on `technical` and `decision` notes
- `scope:` — required on `workflow` notes (`vault` | `tool` | `claude`)
- `doi:`, `authors:`, `year:` — required on `literature` notes

## Status values

| value | meaning |
|-------|---------|
| `active` | current and accurate |
| `draft` | incomplete, do not rely on |
| `superseded` | replaced by another note (link to it) |
| `archived` | project ended; kept for reference |

## Linking conventions

- Internal links: wikilinks only — `[[note-name]]`
- External links: standard markdown — `[text](url)`
- Every permanent note must have at least 2 wikilinks
- First wikilink should point to the project-index or a concept note
- `technical` and `decision` notes must include at least one `file:line` citation

## Tagging conventions

- `project-index` notes: tag with the project name — `[your-project]`
- `concept` notes: tag with the domain — `[<domain>, <subdomain>]`
- `technical` and `decision` notes: tag with project + topic — `[[[your-project]], architecture]`; use a wikilink to the project-index note for the project tag.
- `literature` notes: tag with domain — `[literature, <domain>]`
- `workflow` notes: always include `[workflow]`

## Templates

All templates live in `templates/`. File names match the type:

- [[templates/project-index]]
- [[templates/concept]]
- [[templates/technical]]
- [[templates/decision]]
- [[templates/literature]]
- [[templates/workflow]]
- [[templates/fleeting]]

## Rationale

Keeping `concept` notes project-agnostic means they accumulate value across projects and survive archival. Keeping `technical` notes project-bound means they can be deprecated cleanly when the code changes. `workflow` notes are separated so they can be read by Claude as conventions without being mixed into domain or project content.

The `type: workflow, scope: claude` combination flags notes that Claude should treat as behavioural instructions during sessions — distinct from notes written for the user's own reference.
