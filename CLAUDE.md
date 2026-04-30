# Vault — Instructions for Claude Code

## What is this vault
Centralised knowledge base for all your projects. Persistent memory across sessions.

## Project stacks
List each project subfolder and its stack here. Example:
- Project `data-pipeline`: `<your stack — e.g. Python + Postgres>`

## Workflow Rules and Description

The `workflow/` folder contains conventions used across projects.

**Full taxonomy and conventions:** [[note-type-taxonomy]] — authoritative source for note types, mandatory fields, status values, tagging, and linking standards. Read it before creating any note.

Rules for importing chats into Obsidian: [[chat-import-pipeline]].

Instructions for the graphify skill: [[graphify-community-labeling]] and [[graphify-parser-patches]].

CLAUDE.md vs vault notes — division of labour: [[claude-md-vs-vault-notes]].

### Note creation (summary)
- Use wikilinks: `[[note-name]]` (not markdown links)
- Mandatory YAML frontmatter on every note — use a template from `templates/`
- Filenames in kebab-case: `auth-flow.md`, not `Auth Flow.md`
- 1 concept per permanent note (atomicity)
- Minimum 2 wikilinks per note (dense linking)
- `technical` and `decision` notes must include at least one `file:line` citation

### Note types and home folders
| type | folder | purpose |
|------|--------|---------|
| `project-index` | `permanent/` | Entry point for one project |
| `concept` | `permanent/` | Project-agnostic domain knowledge |
| `technical` | `permanent/` | Architecture, fragilities, design decisions |
| `decision` | `permanent/` | Architectural/methodological choices |
| `literature` | `references/` | One note per paper |
| `workflow` | `workflow/` | Vault conventions and meta-decisions |
| `fleeting` | `fleeting/` | Low-friction dump for TODOs, ideas, open questions — minimal frontmatter, retired within ~14 days |
| `session-log` | `logs/` | Session records — not permanent notes |

### Never do
- Don't delete notes without asking
- Don't use markdown links for internal notes (use wikilinks)
- Don't create notes without frontmatter
- Don't change folder structure without documenting it

## Session Commands

### /resume
When you receive this command:
1. Read the most recent day's session logs in `logs/`.
2. Read decision notes in `permanent/` for the current project — filter by `type: decision` and `project:` matching the project named in the project's `CLAUDE.md`.
3. List `fleeting/` (titles + `created` dates only — do NOT read full bodies unless asked). Surface count, oldest entry, and any note older than 14 days. Read body on demand.
4. Summarise current state and what's left to do; flag stale fleeting notes for retirement.

### /save
When you receive this command:
1. Create a session log at `logs/YYYY-MM-DD-description.md` recording what was done, decisions made, pending items, with wikilinks to created/modified notes.
2. Ask whether any in-flight ideas or TODOs should land in `fleeting/` before committing.
3. Sweep `fleeting/` for retirement candidates (`created` > 14 days). For each, propose:
   - **Promote** → rewrite frontmatter using a `templates/` file, `git mv` to `permanent/` (or `references/` / `workflow/`).
   - **Archive** → `git mv` to `fleeting/archive/` (kept as a record of an idea not pursued).
   - **Delete** → if done or stale.
4. Every 10th `/save`, prompt about chat-history pruning: list `chats/code/*.md` older than 30 days and ask whether to delete. Chats are git-ignored. Recovery after deletion requires re-running `claude-extract` against per-profile session storage. Confirm before deleting.
5. Run `git status` and surface anything unexpected (uncommitted changes outside the vault notes — dirty submodule pointers, stray files) and confirm before staging.
6. Run `git commit` and `git push`.

## Chat Import Pipeline

### Structure
- `chats/code/` → imported Claude Code conversations
- `chats/web/` → imported Claude Web/App conversations
- All chats get `type: chat` frontmatter and a `chat-import` tag

### Filter in Graph View
- `tag:chat-import` → chats only
- `-path:chats` → hide chats

### Mining chats into fleeting notes
The import is automatic; turning chats into vault knowledge is manual. Atomic ideas, TODOs, and open questions land in `fleeting/` with the 3-field frontmatter from `templates/fleeting.md`. Full procedure (cluster heuristic for chunked exports, promotion path, retirement) in [[chat-import-pipeline]].

## Graphify (Codebase Maps)

### Structure
- `graphify/<project>/` → knowledge graph mirror for one project
- Notes are auto-generated — do NOT edit manually

### After every graph rebuild
After any `/graphify` run or `graphify update` that changes community structure, label communities per [[graphify-community-labeling]]:
1. Dump community membership and assign 2–5 word plain-language names
2. Persist to `<project>/graphify-out/.graphify_labels.json` in the `{name, members}` schema
3. Regenerate vault mirror with `to_obsidian(..., community_labels=labels)`
4. Verify: zero `_COMMUNITY_Community N.md` files remain

### In Graph View
- Filter by `path:graphify` → only code nodes
- Filter by `-path:graphify` → hide code nodes
