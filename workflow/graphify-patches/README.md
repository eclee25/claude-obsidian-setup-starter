# graphify-patches

Vault-owned R and Stan AST extractors for [graphifyy](https://github.com/sponsors/safishamsi).

Upstream graphifyy has no R or Stan support. These patches add it by injecting
two functions (`extract_r`, `extract_stan`) plus three surgical edits into the
installed `graphify/extract.py`. Every edit is marker-bounded so the patch
operation is idempotent and reversible.

## Files

| File | Purpose |
|---|---|
| `extractors.py` | Improved `extract_r` + `extract_stan`. Source of truth. Run directly (`python3 extractors.py`) to execute the built-in selftest. |
| `apply.py` | Injects the patches into the installed graphify. Also runs a smoke test after patching. |
| `apply.sh` | Shell wrapper that locates the right Python interpreter (uv tool → pipx → system) and runs `apply.py`. Use this as the automation entry point. |

## Usage

```bash
./apply.sh                 # apply patches + run smoke test (idempotent)
./apply.sh --check         # report patch status (exit 0 = all patched)
./apply.sh --remove        # strip patches (does not delete the backup)
./apply.sh --python <py>   # override the detected interpreter
```

## Post-upgrade automation

After every `pipx upgrade graphifyy` (or `uv tool upgrade graphifyy`),
re-run:

```bash
~/vault/workflow/graphify-patches/apply.sh
```

Options for automating this:

1. **Alias** — add to your shell:
   ```bash
   alias graphify-upgrade='pipx upgrade graphifyy && ~/vault/workflow/graphify-patches/apply.sh'
   ```
2. **Cron / systemd timer** — run `apply.sh` weekly; it's a no-op if patches are
   already in place.
3. **pipx post-upgrade hook** — pipx doesn't support hooks directly, but a
   wrapper script like the alias above is the idiomatic equivalent.

## What the patches fix

See [[graphify-parser-patches]] for the full before/after analysis. Summary:

**R (`extract_r`)**
- Strings and `#` comments stripped before scanning (no more `library(foo)`
  false-positive from a string literal).
- Function body ranges found via paren + brace balance, not "until the next
  top-level def" (was attributing top-level code to the previous function).
- `setMethod()`, `setGeneric()`, `obj$method`, `pkg::name` all recognised.
- `source("a/util.R")` and `source("b/util.R")` stay distinct nodes (they
  previously collapsed onto one id).
- Expanded tidyverse skip list.

**Stan (`extract_stan`)**
- String literals and `/* ... */` block comments stripped before brace
  counting (upstream broke on `print("}")` etc.).
- Function-name lookup uses a bare-name dict, fixing the
  `split("_")[-1]` bug that silently dropped every multi-underscore
  function (`log_lik_gp` → was being searched as `gp`).
- Multi-line function signatures handled.
- Sampling statements (`y ~ my_dist(mu)`) now generate call edges to
  user-defined `_lpdf` / `_lpmf` functions.
- Block ranges tracked via brace-matched ranges, independently for each
  block — no desync when a non-target block sits between two target blocks.
- `#include <angle>` form supported in addition to `#include "quoted"`.

## Safety

- The first time `apply.py` touches `extract.py`, it writes a backup to
  `extract.py.vault-backup` in the same directory. Subsequent runs do not
  overwrite the backup.
- Every patched region is enclosed in marker comments
  (`# vault-patch: …` / `# ── graphify-patches begin (vault) ──`). `--remove`
  strips exactly those regions.
- `apply.py` refuses to patch if the upstream file no longer contains the
  expected anchor points (`_DISPATCH: dict[str, Any] = {`,
  `_EXTENSIONS = {`). Manual inspection required if that happens.
- After patching, the applicator imports `graphify.extract` in the target
  interpreter and runs a representative R and Stan fixture. Non-zero exit on
  any check failure.

## Updating the extractors

Edit `extractors.py`, run the selftest (`python3 extractors.py`), then
re-apply (`./apply.sh`). The applicator replaces the entire footer block on
every run, so changes propagate without needing to remove-then-apply.
