---
title: Chat Import Pipeline
tags: [workflow, claude, chat-import, sync]
created: 2026-04-24
updated: 2026-04-28
status: active
type: workflow
scope: vault
---

# Chat Import Pipeline

Automated pipeline that exports Claude Code sessions from all profiles and imports them into the vault as enriched markdown notes.

## Convention

At the end of every Claude Code session, a Stop hook triggers `~/scripts/sync_claude_obsidian.sh`, which:

1. Runs `claude-extract --all` against each profile (`~/.claude`, `~/.claude-perso`, `~/.claude-gdd`)
2. Exports sessions as markdown to `~/claude-exports/code/`
3. Runs `~/scripts/claude_to_obsidian.py`, which adds YAML frontmatter, auto-tags, and injects wikilinks
4. Moves processed files into `chats/code/` inside the vault

No manual action is required — the sync runs automatically on session end for all three profiles.

## Rationale

Manual export is easy to forget. Hooking into the Stop event ensures every session is captured without relying on the user to remember. Centralising extraction across all profiles avoids missing sessions from the gdd or perso accounts.

## Scope

Vault-wide. The hook is configured in all three `settings.json` files:
- `~/.claude/settings.json`
- `~/.claude-perso/settings.json`
- `~/.claude-gdd/settings.json`

## Shared config structure

Skills and `CLAUDE.md` are shared across profiles via symlinks to `~/dotfiles/claude/`:

```
~/dotfiles/claude/
├── skills/          ← canonical skills directory
├── CLAUDE.md        ← canonical global instructions
└── settings.base.json  ← reference template for per-profile settings
```

Each profile's `skills/` and `CLAUDE.md` are symlinks to this location. To add or update a skill, edit `~/dotfiles/claude/skills/` — all profiles pick it up immediately.

## Git tracking and recovery

`chats/` and `graphify/` are excluded from version control via `.gitignore` — they are auto-generated on every session and would create noisy commits. Only deliberately authored notes (`permanent/`, `references/`, `workflow/`, `templates/`, `logs/`) are tracked in git.

The files still exist locally for Obsidian to use; they are just not versioned.

**Important — `~/claude-exports/code/` does not retain originals.** The sync invokes `claude_to_obsidian.py --move`, which `unlink()`s the export file after writing it into the vault. The vault's `chats/code/` is the only persistent copy of the imported markdown. Recovery after deletion requires re-running `claude-extract` against the per-profile session storage in `~/.claude*/sessions/`. That works for sessions still present in profile storage but is not guaranteed for older or cleared sessions.

## Mining chats into fleeting notes

The pipeline above only handles *import*. Turning chat content into vault knowledge is a manual second step, with `fleeting/` as the low-friction landing pad.

### When
- Ad hoc, when you spot something worth keeping while reviewing chats.
- As a step before `/save` (Claude prompts for it).
- On request: ask Claude to scan recent chats and propose fleeting notes.

### How (Claude-side procedure)
1. Identify candidate chats — focus on the most recent `chats/code/` files first; older sessions decay in usefulness.
2. **Cluster heuristic for chunked exports:** files of size ~33712 B are export-cap chunks. Consecutive numbered files on the same date typically belong to one session — read in clusters, not file-by-file, to preserve context.
3. For each atomic candidate, write `fleeting/<topical-name>.md` using [[templates/fleeting]] (3-field frontmatter, no ceremony). One concept per file.
4. Include a wikilink back to the source chat so provenance survives — e.g. `Source: [[2026-04-28-claude-conversation-log-33]]`.
5. Skip:
   - Pure debugging back-and-forth without reusable insight
   - Meta-conversations about Claude / the vault itself (unless they reveal a workflow worth documenting)
   - Anything already covered by an existing `permanent/` note (check titles first)

### Promotion path
A fleeting note matures into a permanent type via:
1. Rewrite frontmatter to the destination type (`concept` / `technical` / `decision` / `literature` / `workflow`) using the matching template.
2. Apply the destination's rules (≥2 wikilinks; `file:line` citation for `technical`/`decision`).
3. `git mv fleeting/<name>.md permanent/<name>.md` (or `references/`, `workflow/`).
4. Update incoming wikilinks if the filename changes.

### Retirement
Default age threshold: **14 days** from `created`. `/save` and `/resume` surface stale fleeting notes for promotion / archival / deletion. See project [[CLAUDE]] for the exact prompts.

## Related

- [[note-type-taxonomy]] — note types and where chats land in the taxonomy
- [[workflow/note-type-taxonomy]] — authoritative conventions
