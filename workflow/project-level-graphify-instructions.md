---
title: Project-level instructions for graphify
tags:
  - workflow
created: 2026-04-24
updated: 2026-04-28
status: active
type: workflow
scope: vault
---
# Project-level instructions for graphify

Instructions on how to use skill graphify to build project-level graphs.

## Convention

### 3-Layer Query Rule
1. **First:** query `graphify-out/graph.json` or `graphify-out/wiki/index.md`
   to understand code structure and connections
2. **Second:** query the Obsidian vault for decisions, progress, and project context
3. **Third:** only read raw code files when editing
   or when the first two layers don't have the answer

### When to rebuild the graph
- After structural changes (new modules, major refactors)
- Command: `graphify . --update` (only processes modified files)
- The graph is persistent — NO need to rebuild every session

### After re-clustering: label communities
`graphify cluster-only` emits generic `Community N` names. After any re-cluster, follow [[graphify-community-labeling]] (in the vault's `workflow/` folder) to assign 2–5 word semantic labels, persist them to `graphify-out/.graphify_labels.json`, and regenerate the Obsidian vault + `graph.html` + `graph.canvas` with `community_labels=` passed through.

### Do NOT
- Don't manually modify files inside `graphify-out/`
- Don't re-read the entire codebase if the graph already has the information

## Rationale
Use of graphify to improve Claude code navigation of the repo.

## Scope
Where this applies: vault-wide, project-specific, Claude-facing only.

## Related

- [[graphify-community-labeling]] —  [[graphify-parser-patches]]
