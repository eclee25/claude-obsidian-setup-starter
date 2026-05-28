---
title: "2026-05-28 Utility functions and analysis setup"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — Utility functions and analysis setup

## What was done

### `classify_ringer()` extracted to `R/2_clinical_utils.R`

Moved the inline `ringer_bin` `cut()` mutate from the `data-prep` chunk into a dedicated `classify_ringer()` function. Added to pipeline after `clean_ringer()`. Roxygen docstring notes the lowest bin conflates zero Ringer's with low-dose.

### `summarise_culture` replaced with `classify_culture_positive()` (`R/2_clinical_utils.R`)

Replaced the 3-level factor function with a logical: `culture_positive = cat_culture == "VC O1"`. Added to pipeline after `classify_culture(w_agg = "yes")`. Column renamed to `culture_positive_admit` before f2 functions.

### `classify_rdt_positive()` added (`R/2_clinical_utils.R`)

New logical function: `rdt_positive = cat_rdt_o1 == "Positive"`. Added to pipeline after `classify_rdt()`. Column renamed to `rdt_positive_admit`.

### Missing data treatment confirmed

For both logical functions, R `NA` propagates (no RDT/culture recorded). String sentinels — `"Invalid"` (RDT), `"Missing"` / `"VC O-Unknown"` / `"VC non-O1"` (culture) — resolve to `FALSE`, not `NA`. This is intentional: `FALSE` = "not confirmed positive" is the correct interpretation for non-missing classifications.

### `df_analysis` filter moved from `df_clean` to `df_analysis` (`R/4_data_exploration.qmd`)

RDT NA filter previously in `df_clean` moved to `df_analysis`, preserving the full cleaned cohort in `df_clean`. `df_analysis` now filters: `rdt_positive_admit == TRUE`, `!is.na(cat_rdt_o1_discharge)`, and optionally `culture_positive_admit == TRUE` (see below).

### Quarto `params: require_culture` added (`R/4_data_exploration.qmd`)

Two-analysis setup via Quarto params:
- `require_culture: true` (default) — primary analysis: RDT+ at admission AND culture-confirmed VC O1
- `require_culture: false` — sensitivity analysis: RDT+ at admission only

Render commands:
```bash
quarto render R/4_data_exploration.qmd -P require_culture:true
quarto render R/4_data_exploration.qmd -P require_culture:false
```

### Missing columns added to `df_clean` select

`rdt_positive`, `culture_positive`, and `ringer_bin` were not matched by any existing `contains()` pattern and were being silently dropped. Added `contains("rdt_positive")`, `contains("culture_positive")`, and `ringer_bin` explicitly.

### `classify_serotype` logic issue identified (external repo)

`classify_serotype` (not in uvira-sandbox) has two unreachable discordance rules (rules 3 and 7 in `cat_serotype` are dead — OR rules 2 and 6 fire first). Fix proposed: move explicit discordance checks before the OR rules. Tracked in [[classify-serotype-dead-rules]] fleeting note; to be actioned in the relevant repository.

## Decisions made

- Missing data: string sentinels (`"Invalid"`, `"Missing"`, `"VC O-Unknown"`) → `FALSE` in logical columns, not `NA` — see explanation above.
- `df_analysis` filter belongs in `df_analysis`, not `df_clean`

## Pending / open questions

(Carried forward)

- Implement `classify_serotype` discordance fix in the relevant repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` chunk and iterate on any remaining unmatched strings
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose — separate zero level?
- `temp_clean_discharge()` commented out — patches C-12575, C-12557, C-24384 intentionally skipped?
- `ors_f2` factor levels not yet confirmed

## Files changed

- `R/2_clinical_utils.R` — `classify_ringer()`, `classify_culture_positive()`, `classify_rdt_positive()` added; `summarise_culture` replaced
- `R/4_data_exploration.qmd` — pipeline updated; `df_clean`/`df_analysis` filter restructured; Quarto params added; missing columns added to select
- `R/0_download_data.R` — output filenames updated to `2026_05_28`; `ends_with("f5")` added to select

## Related

- [[f2-antibiotic-no-unknown-level]] — f2 antibiotic functions stay binary Yes/No
- [[survival-analysis-restructure-2026-05]] — model covariate context
- [[classify-serotype-dead-rules]] — flagged issue in external repo
- [[uvira-sandbox]] — project index
