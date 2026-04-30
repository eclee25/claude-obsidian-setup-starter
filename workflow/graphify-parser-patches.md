---
title: Graphify R and Stan parser patches
tags: [workflow, graphify, r, stan, ast]
created: 2026-04-24
updated: 2026-04-24
status: active
type: workflow
scope: vault
---

# Graphify R and Stan parser patches

Vault-owned regex extractors for R and Stan that patch into the pipx-installed
`graphifyy` package, replacing in-session-only definitions that got wiped by
every upgrade.

## Convention

The R and Stan AST extractors used by `/graphify` live at
[[graphify-patches/extractors.py]], not inside the distributed graphifyy
package. A small applicator at [[graphify-patches/apply.py]] (with a shell
wrapper [[graphify-patches/apply.sh]]) injects them into the installed
`graphify/extract.py` in three marker-bounded places:

1. The `_DISPATCH` dict inside `extract()` — routes `.R`, `.r`, `.Rmd`,
   `.rmd` to `extract_r` and `.stan` to `extract_stan`.
2. The `_EXTENSIONS` set inside `collect_files()` — adds the same suffixes
   so files are discovered.
3. A footer block at module end — redefines `extract_r` and `extract_stan`
   at module scope. The dispatch dict re-reads these names on every call,
   so the late-bound definitions win.

Every edit is idempotent (re-running applies the current source, no
duplicates accumulate) and reversible (`apply.sh --remove` strips every
marker-bounded region).

**After every `pipx upgrade graphifyy` or `uv tool upgrade graphifyy`,
re-run `workflow/graphify-patches/apply.sh`.** See
[[graphify-patches/README|README]] for alias / cron options.

## Rationale

The prior session added R and Stan extractors directly to the pipx-installed
`graphify/extract.py`. That was convenient but fragile: the next
`pipx upgrade graphifyy` wipes every in-place edit and the patches are gone.
This workflow moves the authoritative copy into the vault so the patches:

- Survive upgrades (re-applied by a single script).
- Are version-controlled alongside the rest of the vault.
- Can be improved iteratively — selftest runs before every apply.
- Are reversible — `--remove` strips markers exactly.

Alternatives considered and rejected:

- **Upstream PR** — requires coordinating with the graphifyy maintainer;
  turnaround unknown; the R / Stan surface may not match what upstream wants
  to commit to. Still a worthy future move, but not the short path.
- **Fork graphifyy + `pipx install --force`** — forces us to carry the full
  graphifyy maintenance burden for just two extractor functions.
- **Monkey-patch via sitecustomize** — works for function replacement but
  cannot modify the `_DISPATCH` dict because it's built inside a function
  each call; would need a separate registration hook upstream doesn't have.

Injecting marker-bounded edits into `extract.py` gives us the replacement
surface we need without carrying unrelated maintenance.

## Scope

Applies to the local pipx/uv installation of `graphifyy` on any machine
where this vault is checked out. Running `apply.sh` is a manual operation
tied to upgrades; it is not invoked automatically during `/graphify` runs.

## What the patches fix

Known bugs in the prior in-place versions (which the vault copy addresses):

| Parser | Bug | Fix |
|---|---|---|
| R | `library(foo)` inside a string literal counted as an import | Strip string contents before scanning call sites |
| R | Function body range = "until next top-level def"; mis-attributed top-level code to the previous function | Track paren-then-brace depth from `function(…)` to matching `}` |
| R | `setMethod`, `setGeneric`, `obj$method`, `pkg::name` not recognised | Added dedicated call-site regexes reading from the string-preserving view |
| R | `source("a/util.R")` and `source("b/util.R")` collapsed to one node id | ID built from full path, not just stem |
| Stan | `nid.split("_")[-1]` dropped every multi-underscore function silently (`log_lik_gp` → `gp`) | Use a bare-name dict keyed at def time |
| Stan | Brace counting happened on raw source; `print("}")` broke block tracking | Strip strings + `/* */` block comments first |
| Stan | Multi-line function signatures missed | Join consecutive lines until `{` or `;` before matching |
| Stan | Sampling statements `y ~ my_dist(mu)` produced no edges | Added `~`-statement scanner with `_lpdf`/`_lpmf` fallback |
| Stan | `#include functions/file.stan` (bare, no quotes) not matched | Regex extended to handle bare filenames in addition to `<…>` and `"…"` forms |
| Stan | `#include` target node ID (`functions_file_stan`) didn't match the extracted file's ID (`analysis_stan_functions_file_stan`) | Resolve include path relative to the including file (`path.parent / ref_path`) before computing `_make_id` |

## Cache invalidation after patch upgrades

After re-applying patches, cache entries written with the old extractor are
stale but still served by graphify (cache is keyed on file hash, not extractor
version). Manually clear affected entries:

```python
from graphify.cache import file_hash, cache_dir
from pathlib import Path
for f in ["analysis/stan/ode_inference_modular.stan", "notebooks/monitor_sampling_config.Rmd"]:
    p = Path(f)
    entry = cache_dir(Path('.')) / f'{file_hash(p, root=Path("."))}.json'
    if entry.exists():
        entry.unlink()
        print(f"cleared: {f}")
```

Or delete all cache entries to force a full re-extraction (fast for code-only runs):
`rm graphify-out/cache/*.json`

See [[graphify-patches/README|graphify-patches/README.md]] for the full
before/after and [[graphify-patches/extractors.py|extractors.py]] for the
implementation with an inline selftest.

## Examples

```bash
# Normal upgrade workflow
pipx upgrade graphifyy
~/vault/workflow/graphify-patches/apply.sh

# Verify
~/vault/workflow/graphify-patches/apply.sh --check

# Temporary revert (keeps backup)
~/vault/workflow/graphify-patches/apply.sh --remove
```

## Related

- [[note-type-taxonomy]] — vault rules this note follows
- [[graphify-patches/README|graphify-patches/README]] — operational how-to
- [[graphify-patches/extractors.py|extractors.py]] — improved parsers + selftest
- [[graphify-patches/apply.py|apply.py]] — patch applicator
