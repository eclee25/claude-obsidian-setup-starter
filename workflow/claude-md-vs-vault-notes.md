---
title: CLAUDE.md vs Vault Notes — Division of Labour
tags: [workflow, claude, zettelkasten]
created: 2026-04-23
updated: 2026-04-23
status: active
type: workflow
scope: vault
---

# CLAUDE.md vs Vault Notes — Division of Labour

CLAUDE.md files and vault notes serve different roles and should not duplicate each other. CLAUDE.md owns instructions and pointers; vault notes own knowledge.

## Convention

**CLAUDE.md files** (project and vault level) should contain:
- Behavioural instructions (what Claude must or must not do)
- Session commands (`/resume`, `/save`)
- Critical invariants that must always be in context — things that break silently if forgotten (e.g. `omega_2 * 2` in boost-root models, Stan recompilation warning)
- One-line pointers to where knowledge lives in the vault or graph
- Quick-reference summaries where a navigation step would be wasteful for routine tasks

**Vault permanent and workflow notes** should contain:
- Architecture detail and design rationale
- Decisions and their outcomes
- Domain concepts that accumulate across projects
- Conventions about the note-taking system itself

## Rationale

CLAUDE.md files are loaded automatically at session start — they are always in context at zero cost. Vault notes require a navigation step (a tool call). Putting detailed knowledge in CLAUDE.md wastes tokens every session; putting instructions in vault notes means Claude may miss them if it does not navigate there.

The redundancy that matters: once a permanent note fully covers an Architecture section in a project CLAUDE.md, that section should be replaced with a one-line pointer. The permanent notes earn their place by making CLAUDE.md shorter over time.

The redundancy that is intentional: a quick-reference summary in CLAUDE.md that duplicates a vault note is fine when it avoids a navigation step for routine decisions. The CLAUDE.md version should always defer to the vault note as authoritative for full detail.

## How to apply

When writing or updating a CLAUDE.md:
- If a section describes *what to do* → keep it in CLAUDE.md
- If a section describes *how something works* and a permanent note exists → replace with a pointer
- If a section describes *how something works* and no permanent note exists yet → keep it in CLAUDE.md temporarily, mark it as a candidate for migration

When writing permanent notes:
- Once complete, update the corresponding CLAUDE.md section to a one-line pointer
- Do not maintain both in parallel indefinitely

## Practical path

Write the permanent notes first. Refactor CLAUDE.md sections into pointers only once the notes are complete and accurate. Do not refactor prematurely.

## Related

- [[workflow/note-type-taxonomy]] — full note type definitions and conventions
