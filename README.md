# Claude Code Vault — Template Setup

A template Obsidian vault and tooling layer that gives [Claude Code](https://claude.com/claude-code) durable, structured memory across sessions and projects.

This repo is a derivative of [lucasrosati/claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup) and keeps its core ideas: an Obsidian vault as Claude's long-term memory, [graphify](https://github.com/sponsors/safishamsi) as a tree-sitter knowledge graph for source code, and an automatic chat-import pipeline. It adds:

- A formal **note-type taxonomy** (concept / technical / decision / literature / workflow / fleeting / project-index) with mandatory frontmatter and templates.
- **R and Stan extractor patches** for graphify (upstream graphify covers neither language) with a reversible, idempotent applicator that survives `pipx upgrade`.
- A **community labelling workflow** for graphify clusters that survives re-clustering — communities keep their plain-language names across rebuilds via a member-keyed `.graphify_labels.json` and Jaccard carry-forward in a post-commit hook.
- A **multi-profile** layout (`.claude`, `.claude-acct1`, `.claude-acct2`) sharing skills and `CLAUDE.md` via dotfiles symlinks.
- Explicit `/save` and `/resume` slash commands with a `fleeting/` retirement sweep.

Clone this repo as your starting vault, rename the dummy `data-pipeline/` project, and you're ready.

---

## Table of contents

- [What you get](#what-you-get)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Vault structure](#vault-structure)
- [Note-type taxonomy](#note-type-taxonomy)
- [The two CLAUDE.md files](#the-two-claudemd-files)
- [Session commands: `/resume` and `/save`](#session-commands-resume-and-save)
- [Chat import pipeline](#chat-import-pipeline)
- [Graphify integration](#graphify-integration)
  - [R + Stan parser patches](#r--stan-parser-patches)
  - [Community labelling that survives re-clustering](#community-labelling-that-survives-re-clustering)
  - [Project-level post-commit hook](#project-level-post-commit-hook)
- [Multi-profile setup (optional)](#multi-profile-setup-optional)
- [Day-to-day workflow](#day-to-day-workflow)
- [Adapting the template to your project](#adapting-the-template-to-your-project)

---

## What you get

| Layer | What it is | Why |
|---|---|---|
| Obsidian vault | Centralised markdown notes with strict frontmatter and wikilinks | Durable, queryable memory for both Claude and you |
| `CLAUDE.md` files (vault + per-project) | Behavioural instructions auto-loaded at session start | Always-on context that shapes Claude's behaviour |
| Note templates | One template per note type, in `templates/` | Consistent shape so Claude can parse and you can promote freely |
| `/save` and `/resume` | Slash commands defined in `CLAUDE.md` | One command at session start and end ⇒ continuity |
| Chat import pipeline | Stop hook → extract → enrich → land in `chats/code/` | Every session is captured without manual export |
| Graphify | AST-based knowledge graph of your codebase | Claude navigates the graph (`graph.json`, `wiki/`) before reading raw source — large token savings |
| Graphify patches | Vault-owned R + Stan extractors and applicator | Adds languages graphify doesn't ship; survives upgrades |
| Community labels | LLM-assigned semantic names persisted to `.graphify_labels.json` | Each graph community appears in Obsidian as `_COMMUNITY_<plain-language name>.md`, not `Community 7` |

---

## Prerequisites

Required:

- [Claude Code](https://claude.com/claude-code) installed and authenticated.
- [Obsidian](https://obsidian.md) (free).
- Python ≥ 3.10.
- Git.

Recommended:

- [pipx](https://pipx.pypa.io) (or [uv](https://github.com/astral-sh/uv) `tool install`) for isolated Python tools.
- [`graphifyy`](https://pypi.org/project/graphifyy/) — `pipx install graphifyy`.
- [`claude-conversation-extractor`](https://pypi.org/project/claude-conversation-extractor/) — `pipx install claude-conversation-extractor` (provides `claude-extract`).

Optional, only if you work in R/Stan:

- The R + Stan parser patches in `workflow/graphify-patches/`.

---

## Quick start

```bash
# 1. Clone the template
git clone https://github.com/<you>/claude-code-vault.git ~/vault
cd ~/vault

# 2. Open the vault in Obsidian (File → Open vault as folder)

# 3. Tell Claude Code about it
ln -s ~/vault/CLAUDE.md ~/.claude/CLAUDE.md   # or copy if you prefer

# 4. Install the Python tools
pipx install graphifyy
pipx install claude-conversation-extractor

# 5. (R/Stan users only) apply the graphify patches
~/vault/workflow/graphify-patches/apply.sh

# 6. Rename the dummy project
git mv data-pipeline my-real-project
sed -i 's/data-pipeline/my-real-project/g' \
  permanent/data-pipeline.md \
  CLAUDE.md
git mv permanent/data-pipeline.md permanent/my-real-project.md

# 7. Initialise your project's graph
cd ~/code/my-real-project
graphify . --obsidian --obsidian-dir ~/vault/graphify/my-real-project

# 8. Install the post-commit hook in your project (incremental rebuilds + label carry-forward)
cp ~/vault/scripts/post-commit-graphify .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# 9. Wire the chat-import Stop hook into each Claude profile's settings.json
#    (see "Chat import pipeline" below)
```

You're ready. Open Claude Code in your project, type `/resume`, and it will summarise the (empty) state and tell you what to do next.

---

## Vault structure

```
vault/
├── CLAUDE.md                 # Vault-level instructions (auto-loaded by Claude)
├── README.md                 # Public-facing readme of YOUR vault
├── .gitignore                # Excludes chats/ and graphify/ generated files
│
├── scripts/                  # Shipped tooling
│   ├── sync_claude_obsidian.sh    # Stop-hook entry point (extract → enrich → land)
│   ├── claude_to_obsidian.py      # Frontmatter / tag / wikilink processor
│   └── post-commit-graphify       # Project-level git hook for incremental rebuilds
│
├── permanent/                # Permanent notes — concepts, technical, decisions, project-indexes
│   └── data-pipeline.md      # Project-index for the dummy project
│
├── references/               # Literature notes, one per paper
├── workflow/                 # Vault conventions and meta-docs (Claude reads these)
│   ├── note-type-taxonomy.md
│   ├── chat-import-pipeline.md
│   ├── claude-md-vs-vault-notes.md
│   ├── graphify-community-labeling.md
│   ├── graphify-parser-patches.md
│   ├── project-level-graphify-instructions.md
│   └── graphify-patches/     # Idempotent R + Stan extractor patches
│       ├── apply.sh
│       ├── apply.py
│       ├── extractors.py
│       └── README.md
│
├── templates/                # One per note type
│   ├── concept.md
│   ├── decision.md
│   ├── technical.md
│   ├── literature.md
│   ├── workflow.md
│   ├── project-index.md
│   ├── fleeting.md
│   └── default-note.md
│
├── fleeting/                 # Low-friction TODOs / open questions; auto-retired ~14 days
│   └── archive/              # Things that didn't graduate but are worth keeping
│
├── inbox/                    # Manual unprocessed captures (rare)
├── logs/                     # YYYY-MM-DD-description.md session logs
│
├── chats/                    # Auto-generated, GIT-IGNORED
│   ├── code/                 # Imported Claude Code sessions
│   └── web/                  # Imported Claude Web sessions
│
├── graphify/                 # Auto-generated, GIT-IGNORED
│   └── data-pipeline/        # Per-project mirror of graphify export
│
└── data-pipeline/            # Dummy project working copy (replace with yours)
    └── CLAUDE.md             # Project-level instructions
```

`chats/` and `graphify/` are excluded from git via `.gitignore` — they are auto-generated and would create noisy commits. Only deliberately authored content (`permanent/`, `references/`, `workflow/`, `templates/`, `logs/`, `fleeting/`) is tracked.

---

## Note-type taxonomy

Seven note types. Each has a home folder, a scope, and mandatory frontmatter fields. The full table:

| type | folder | scope | purpose |
|------|--------|-------|---------|
| `project-index` | `permanent/` | project | Entry point for one project. One note per project. |
| `concept` | `permanent/` | domain | Project-agnostic domain knowledge (e.g. "rate limiting", "Bayesian inference"). Survives project archival. |
| `technical` | `permanent/` | project | Non-obvious architecture, fragilities, design decisions derivable only from reading the code carefully. |
| `decision` | `permanent/` | project | Architectural or methodological choices: context, alternatives, rationale, outcome. |
| `literature` | `references/` | domain | One note per paper. Claim, mechanism, relevance, project appearances. |
| `workflow` | `workflow/` | vault | Conventions and decisions about the note-taking system itself. |
| `fleeting` | `fleeting/` | any | Low-friction dump for TODOs, ideas, open questions. Promoted, archived, or deleted within ~14 days. |

Session logs (`type: session-log`) live in `logs/` and are not considered permanent notes.

### Mandatory frontmatter

All non-fleeting notes:

```yaml
---
title: Note Name
tags: [topic, project]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active     # active | draft | superseded | archived
type: <one of the seven>
---
```

Additionally:

- `project:` on `technical` and `decision` notes
- `scope: vault | tool | claude` on `workflow` notes
- `doi:`, `authors:`, `year:` on `literature` notes

`fleeting` notes need only `title`, `type: fleeting`, `created`. No tag minimum, no wikilink minimum, no `file:line` requirement. The point is to capture before the idea evaporates.

### Linking and tagging

- Internal links: wikilinks only — `[[note-name]]`. External links: standard markdown.
- Permanent notes need ≥2 wikilinks. The first should point to a project-index or concept note.
- `technical` and `decision` notes must include at least one `path/to/file.ext:line` citation.
- Tag conventions: project-index notes carry the project name as a tag; concept notes carry their domain; `technical`/`decision` carry project + topic; `literature` carries domain + `literature`; workflow notes always include `workflow`.

The full taxonomy lives at `workflow/note-type-taxonomy.md` and is the authoritative source — read it before creating any note.

### Status values

| value | meaning |
|-------|---------|
| `active` | current and accurate |
| `draft` | incomplete, do not rely on |
| `superseded` | replaced by another note (link to it) |
| `archived` | project ended; kept for reference |

---

## The two CLAUDE.md files

Two `CLAUDE.md` files do different jobs:

1. **Vault-level** (`~/vault/CLAUDE.md`, symlinked or copied to `~/.claude/CLAUDE.md`) — global instructions, note-type rules, `/save` and `/resume`. Loaded for every Claude Code session.
2. **Project-level** (`<project>/CLAUDE.md`) — project-specific: stack, the 3-layer query rule for graphify, "do nots" specific to that codebase, pointers to its key permanent notes. Loaded only when Claude is invoked inside that project.

The division of labour:

- **CLAUDE.md** owns *instructions and pointers* — what to do, what not to do, where knowledge lives.
- **Vault notes** own *knowledge* — architecture, decisions, concepts, design rationale.

Why: CLAUDE.md is auto-loaded at session start (zero-cost context). Vault notes require a navigation step (a tool call). Putting detailed knowledge in CLAUDE.md wastes tokens every session; putting instructions in vault notes risks Claude missing them. Once a permanent note fully covers an architecture section in a project CLAUDE.md, replace that section with a one-line pointer. Permanent notes earn their place by making CLAUDE.md shorter over time.

Full reasoning: `workflow/claude-md-vs-vault-notes.md`.

---

## Session commands: `/resume` and `/save`

Both are defined in vault `CLAUDE.md` and triggered by typing `/resume` or `/save` to Claude Code.

### `/resume`

Run at the start of a session. Claude:

1. Reads the most recent day's session logs in `logs/`.
2. Reads decision notes for the current project (filters `permanent/` by `type: decision` and `project:` matching the project from the project's `CLAUDE.md`).
3. Lists `fleeting/` (titles + `created` dates only — body on demand). Surfaces count, oldest entry, and any note older than 14 days.
4. Summarises current state and what's left to do; flags stale fleeting notes for retirement.

### `/save`

Run at the end of a session. Claude:

1. Creates `logs/YYYY-MM-DD-description.md` with what was done, decisions, pending items, and wikilinks to created/modified notes.
2. Asks whether any in-flight ideas or TODOs should land in `fleeting/` before committing.
3. Sweeps `fleeting/` for retirement candidates (`created` > 14 days). For each, proposes:
   - **Promote** → rewrite frontmatter using a `templates/` file, `git mv` to `permanent/` (or `references/` / `workflow/`).
   - **Archive** → `git mv` to `fleeting/archive/`.
   - **Delete** → if done or stale.
4. Every 10th `/save`, prompts about chat-history pruning (lists `chats/code/*.md` older than 30 days).
5. Runs `git status` and surfaces anything unexpected before staging — uncommitted changes outside the vault notes (dirty submodule pointers, stray files) are confirmed before staging.
6. Runs `git commit` and `git push`.

The slash commands aren't magic — they're prompts written into vault `CLAUDE.md` that Claude follows. Edit them in your fork to taste.

---

## Chat import pipeline

A Stop hook at the end of every Claude Code session runs `scripts/sync_claude_obsidian.sh` (shipped in this repo), which:

1. Runs `claude-extract --all` against each profile (`~/.claude`, `~/.claude-perso`, `~/.claude-gdd` if you use them).
2. Exports sessions as markdown to `~/claude-exports/code/`.
3. Runs `scripts/claude_to_obsidian.py` (shipped) — adds YAML frontmatter, auto-tags, and injects wikilinks for vault notes referenced in the chat.
4. Moves processed files into `chats/code/` inside the vault. The export folder is left empty (`--move`), so **the vault's `chats/code/` is the only persistent copy**. Recovery requires re-running `claude-extract` against per-profile session storage in `~/.claude*/sessions/` — fine for sessions still present, not guaranteed for older or cleared sessions.

Both scripts respect env vars (`CLAUDE_VAULT_DIR`, `CLAUDE_EXPORT_DIR`, `CLAUDE_PROFILES`); defaults assume the vault at `~/vault`. Wire it up in each profile's `~/.claude*/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "command": "bash ~/vault/scripts/sync_claude_obsidian.sh" }
    ]
  }
}
```

To extend keyword → tag mapping for your stack, edit `KEYWORD_TAG_MAP` at the top of `claude_to_obsidian.py`. The shipped map is illustrative only — heavy on web/JS/Python keywords for legibility — and most users will replace most of it with their own vocabulary.

`chats/` is git-ignored. Filter Obsidian's graph view by `tag:chat-import` to see chats only, or `-path:chats` to hide them.

### Mining chats into vault knowledge

Import is automatic; turning chat content into permanent knowledge is a manual second step. The flow:

1. Spot something worth keeping while reviewing a recent `chats/code/` file (or ask Claude to scan and propose).
2. Write `fleeting/<topical-name>.md` using `templates/fleeting.md`. Include a wikilink back to the source chat (e.g. `Source: [[2026-04-28-claude-conversation-log-33]]`).
3. Within ~14 days, `/save` will surface it for promotion (rewrite frontmatter to a permanent type, `git mv` to `permanent/`), archival, or deletion.

Cluster heuristic for chunked chat exports: files ~33 KB are export-cap chunks; consecutive numbered files on the same date typically belong to one session — read in clusters, not file-by-file.

---

## Graphify integration

[Graphify](https://github.com/sponsors/safishamsi) builds a tree-sitter AST graph of your codebase so Claude navigates the graph instead of raw source. Each subsection below points to the authoritative vault note for full detail.

### Seed the graph

Run once per project: `graphify . --obsidian --obsidian-dir ~/vault/graphify/<project>`. Produces `graphify-out/{graph.json, graph.html, GRAPH_REPORT.md, wiki/, cache/}` and a per-node mirror in the vault.

### 3-layer query rule

Graph first → vault notes second → raw code last. Never edit `graphify-out/` by hand. Full rule and rationale: `workflow/project-level-graphify-instructions.md`.

### Rebuild policy

`graphify . --update` re-processes only modified files. The post-commit hook handles incremental rebuilds automatically (see below).

### R + Stan parser patches

Upstream graphify covers neither language. Apply the vault-owned patches once with `workflow/graphify-patches/apply.sh`, and re-apply after every `pipx upgrade graphifyy`. Full rationale, fixes, and `--check` / `--remove` flags: `workflow/graphify-parser-patches.md` and `workflow/graphify-patches/README.md`.

### Community labelling

After clustering, communities get plain-language names persisted to `graphify-out/.graphify_labels.json` in a member-keyed schema (`{cid: {name, members}}`) so they survive re-clusters. Full procedure (initial relabel + the common partial-relabel case): `workflow/graphify-community-labeling.md`.

### Post-commit hook

`scripts/post-commit-graphify` (shipped) re-clusters on pipeline-touching commits, carries names forward via Jaccard match against `members`, and regenerates the vault mirror. Install in your project:

```bash
cp scripts/post-commit-graphify <your-project>/.git/hooks/post-commit
chmod +x <your-project>/.git/hooks/post-commit
```

Tune `GRAPHIFY_VAULT_MIRROR`, `GRAPHIFY_TARGET_RE`, and `GRAPHIFY_FILE_GLOBS` (env or in-file) for your project layout. **The shipped defaults are R/Stan-flavoured** (`analysis/`, `tests/`, `notebooks/` with extensions `.R/.sh/.stan/.Rmd/.qmd`). Worked overrides for other stacks:

```bash
# Python
export GRAPHIFY_TARGET_RE='^(src/|tests/).*\.py$'
export GRAPHIFY_FILE_GLOBS='src/**/*.py tests/**/*.py'

# TypeScript / Node
export GRAPHIFY_TARGET_RE='^(src/|app/|tests/).*\.(ts|tsx|js|jsx)$'
export GRAPHIFY_FILE_GLOBS='src/**/*.ts src/**/*.tsx app/**/*.tsx tests/**/*.ts'
```

The hook warns on stderr when communities drift; relabel procedure is in `workflow/graphify-community-labeling.md`.

---

## Multi-profile setup (optional)

If you run multiple Claude profiles (e.g. work and personal accounts), share skills and `CLAUDE.md` via dotfiles symlinks:

```
~/dotfiles/claude/
├── skills/             ← canonical skills directory
├── CLAUDE.md           ← canonical global instructions
└── settings.base.json  ← reference template for per-profile settings
```

Then each profile becomes a thin shell:

```bash
mkdir -p ~/dotfiles/claude
cp -r ~/.claude/skills ~/dotfiles/claude/skills
cp ~/.claude/CLAUDE.md ~/dotfiles/claude/CLAUDE.md

for prof in ~/.claude ~/.claude-acct1 ~/.claude-acct2; do
    rm -rf "$prof/skills" "$prof/CLAUDE.md"
    ln -s ~/dotfiles/claude/skills "$prof/skills"
    ln -s ~/dotfiles/claude/CLAUDE.md "$prof/CLAUDE.md"
done
```

To add or update a skill or change global instructions, edit `~/dotfiles/claude/` once — every profile picks it up. Per-profile `settings.json` (with the Stop hook) stays separate.

---

## Day-to-day workflow

```text
Open Claude Code in your project
   │
   ▼
/resume                            ← summarises recent logs, decisions, fleeting state
   │
   ▼
Work on code
   │  Claude queries graphify first, then vault, then raw source
   ▼
Capture stray ideas/TODOs in fleeting/   ← either you or Claude does this
   │
   ▼
git commit                         ← post-commit hook re-clusters and updates labels if pipeline files changed
   │
   ▼
/save                              ← writes session log, sweeps fleeting/, commits, pushes
   │
   ▼
Stop hook fires                    ← chat-import pipeline lands the session in chats/code/
```

A typical week then layers on:

- **Promote stale fleeting notes** during `/save`. Don't leave them past 14 days.
- **Re-name drifted communities** when the post-commit hook warns.
- **Promote permanent notes** until the project's `CLAUDE.md` shrinks to mostly pointers (the test of a healthy vault).

---

## Adapting the template to your project

1. Replace the `data-pipeline/` folder with your project (or remove it and add yours as a git submodule).
2. Edit `permanent/data-pipeline.md` (the project-index) to describe your project. Rename the file with `git mv`.
3. Edit the project's `CLAUDE.md`:
   - Stack and entry points
   - 3-layer query rule (already templated)
   - Anti-patterns specific to your codebase
   - Pointers to its first technical / decision notes (you'll write these as you go)
4. Run `graphify . --obsidian --obsidian-dir ~/vault/graphify/<your-project>` once to seed the graph.
5. If R/Stan: run `workflow/graphify-patches/apply.sh` once.
6. Set up the post-commit hook in your project (template at `workflow/graphify-community-labeling.md`).
7. First `/save` will create your first session log. From there it grows.

---

## Credits

Based on [lucasrosati/claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup). Major additions: note-type taxonomy and templates, R/Stan graphify patches, community-labelling workflow with Jaccard carry-forward, multi-profile dotfiles layout, explicit fleeting-note retirement, and the divisional rule between `CLAUDE.md` and vault notes.

[graphifyy](https://pypi.org/project/graphifyy/) by [@safishamsi](https://github.com/sponsors/safishamsi). [`claude-conversation-extractor`](https://pypi.org/project/claude-conversation-extractor/) for chat export.
