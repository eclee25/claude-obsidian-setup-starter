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

## Code Change Policy (all projects)

Distinguish between **code changes** and **domain/content logic changes** before acting:

- **Code changes** (implement directly): refactoring, syntax fixes, renaming, performance improvements, rendering bugs, test fixes — correctness is purely technical.
- **Domain/content logic changes** (describe the issue and options first, implement only after explicit approval): anything that alters what a variable *means* or *captures*, classification rules, inclusion/exclusion criteria, clinical or scientific thresholds, model covariate definitions, how uncertain/unknown cases are handled. These require subject matter expertise to evaluate and must not be changed unilaterally.

When in doubt about which category a change falls into, treat it as domain logic and ask first.

## Session Commands

### /resume
When you receive this command:
1. Read the most recent day's session logs in `logs/`.
2. Read decision notes in `permanent/` for the current project — filter by `type: decision` and `project:` matching the project named in the project's `CLAUDE.md`.
3. List `fleeting/` (titles + `created` dates only — do NOT read full bodies unless asked). Surface count, oldest entry, and any note older than 14 days. Read body on demand.
4. Count files in `chats/code/`. If the count exceeds **500**, surface this as a flag and remind the user that a chat-folder sweep is due (see `/save` step 7a). Do not act unless asked.
5. Check for `<project>/graphify-out/LABELS_STALE` for the active project. If it exists, surface its contents as a flag: graphify community labels drifted since the last commit and a relabel pass is needed.
6. Summarise current state and what's left to do; flag stale fleeting notes for retirement.

### /save
When you receive this command:
1. Create a session log at `logs/YYYY-MM-DD-description.md` recording what was done, decisions made, pending items, with wikilinks to created/modified notes.
2. Ask whether any in-flight ideas or TODOs should land in `fleeting/` before committing.
3. Sweep `fleeting/` for retirement candidates (`created` > 14 days). For each, propose:
   - **Promote** → rewrite frontmatter using a `templates/` file, `git mv` to `permanent/` (or `references/` / `workflow/`).
   - **Archive** → `git mv` to `fleeting/archive/` (kept as a record of an idea not pursued).
   - **Delete** → if done or stale.
4. **Current session chat.** Ask the user whether to keep or delete the chat note for the current session (if one exists in `chats/code/`). Default: delete, since the session log captures the durable knowledge. Confirm before deleting.
5. Chat folder maintenance:
   a. **Size-triggered sweep (any /save).** Count files in `chats/code/`. If the count exceeds **500**, propose a mid-depth sweep: deduplicate by content hash, mine the unique chats for atomic ideas/TODOs/open questions worth landing as fleeting notes (per [[chat-import-pipeline]] §Mining), then delete the folder contents. Confirm with the user before deleting.
   b. **Age-triggered prune (every 10th /save).** Prompt about chat history pruning: list `chats/code/*.md` older than 30 days and ask whether to delete. Confirm before deleting.
   c. Chats are git-ignored. **Recovery after deletion requires re-running `claude-extract`** against per-profile session storage — the export folder `~/claude-exports/code/` is intentionally emptied by the sync (`--move`), so the vault's `chats/code/` is the only persistent copy.
6. Run `git status` and surface anything unexpected (uncommitted changes outside the vault notes — dirty submodule pointers, stray files) and confirm before staging.
7. Run `git commit` and `git push`.

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
