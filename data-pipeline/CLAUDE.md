# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Template note.** This is the project-level `CLAUDE.md` for the dummy `data-pipeline` project that ships with the vault template. Sections marked `<…>` are placeholders — fill them in for your real project, or delete the section entirely if it doesn't apply. The structure is borrowed from a real R+Stan project (Bayesian epidemiology) and stripped of domain specifics; keep what's useful, drop what isn't.

## Project Overview

`<One-paragraph description: what this project does, who uses it, what its main output is.>`

**Active pipeline:** `<entry directory and the way it's invoked>`
**Legacy code:** `<directory of archived code, if any. Note here whether Claude should read it.>`

## Pipeline Execution

`<Replace this block with the actual commands a teammate would run end-to-end. The example below is configuration-driven; collapse to a single command if your pipeline is simpler.>`

```bash
# 1. <Step 1 description>
<command-1>

# 2. <Step 2 description>
<command-2>

# 3. <Step 3 description>
<command-3>
```

## Architecture

### Configuration System

`<Describe how the pipeline is configured: defaults, overrides, env vars, YAML files. Pointers to the relevant files only — full detail belongs in a permanent note.>`

- `<config defaults file>` — baseline defaults
- `<configs/ override directory>` — per-run overrides
- Key config fields: `<list>`

### Modules / Components

`<List the main code modules with one-line purposes. Pointers only.>`

- `<src/foo.py>` — `<purpose>`
- `<src/bar.py>` — `<purpose>`

### Data Flow

```
<input data sources>
  -> <step 1 script>
  -> <intermediate artefact>
  -> <step 2 script>
  -> <final artefact>
```

### Key Parameters / Inputs

`<Table of the parameters or inputs that matter most when answering questions about the system. Empty in the template; fill in or delete.>`

| Parameter / input | Description |
|---|---|
|  |  |

### Key Dates / Constants

`<Project-specific anchor dates, version cutoffs, or constants that are easy to forget. Delete if not applicable.>`

## Key Dependencies

`<List the third-party libraries or services the project depends on, with one-line notes about why each is load-bearing.>`

## Test Suite

`<If you have tests, describe how to run them and what they cover. Delete if not applicable.>`

```bash
<test command>
```

## Cluster / Production Execution

`<If the project runs on an HPC cluster, in CI, or under a job scheduler, describe the entry point. Delete if not applicable.>`

## Context Navigation (Graphify)

**DO NOT** read source files at first pass when answering a question. Follow [[project-level-graphify-instructions]]:

1. **First** — query `graphify-out/graph.json` or `graphify-out/wiki/index.md` for code structure and connections.
2. **Second** — query the vault for decisions, progress, and project context (`permanent/`, `references/`).
3. **Third** — read raw code only when editing, or when the first two layers don't have the answer.

**Scope** — the graphify graph for this project covers exactly:

- `<directory 1>` — `<what's in it>`
- `<directory 2>` — `<what's in it>`

All other top-level directories (`<list, e.g. data/, build/, generated/>`) are excluded via `.graphifyignore`. The git post-commit hook installed from `scripts/post-commit-graphify` and any manual `graphify` rebuild must use this same scope.

## Instructions

`<Optional. Personal guardrails for how Claude should behave inside this project. Delete or rewrite to taste — this is template-author preference, not a vault-wide convention.>`

- Don't take initiative on changes outside what's explicitly asked.
- Don't read raw data files in `<data/>` (privacy / size / IO cost).
- Always follow the 3-layer query rule above before reading source.
