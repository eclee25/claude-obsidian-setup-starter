---
title: "2026-05-22 Descriptive stats for any/ineffective antibiotics and Model 3 extensions"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-22"
type: session-log
project: uvira-sandbox
---

# 2026-05-22 — Descriptive stats for any/ineffective antibiotics and Model 3 extensions

## What was done

### Model 3: Ringer-based severity models added (`R/4_data_exploration.qmd:1056`)

Added three new models (3g, 3h, 3i) to `model3_spec` that mirror 3b, 3c, and 3d with `dehydration` replaced by `ringer_bin`. Rationale: dehydration is assessed subjectively at admission and is prone to inter-observer variability; Ringer's lactate volume is an objective, quantitative proxy for severity. The two variables are expected to be collinear (see existing 3e). The series now has 9 models (a1, a2, b–i).

- **3g** — `age_bin_f1 + sex_f1 + ringer_bin + t_onset_admit` (mirrors 3b)
- **3h** — `+ cat_antibiotics_uvira_f2` (mirrors 3c, primary)
- **3i** — `+ cat_antibiotics_uvira_f1 + cat_antibiotics_uvira_f2` (mirrors 3d)

### `bold_p` in `tbl-model3-summary` fixed (`R/4_data_exploration.qmd:1178`)

`bold_p()` hardcodes its lookup to the column name `"p.value"`. After `tbl_merge()`, gtsummary renames p-value columns to `p.value_1`, `p.value_2`, etc., so `bold_p()` errors post-merge and does not carry through pre-merge. Fix: replaced `bold_p()` with a `purrr::reduce()` + `rlang::inject()` loop that calls `modify_table_styling()` for each `p.value_*` column in the merged table individually. See [[quarto-results-asis-yaml-pitfall]] for the related rendering notes.

### Descriptive statistics: any/ineffective antibiotic use added (`R/4_data_exploration.qmd`)

**`tab-descrip` expanded**: Added `cat_antibiotics_any_f1`, `cat_antibiotics_ineffUvira_f1`, `cat_antibiotics_any_f2`, `cat_antibiotics_ineffUvira_f2` to the summary table with labels ("Any/Effective/Ineffective antibiotic prior to admission / during CTC stay"). Row-group assignments updated for both "Status at admission" and "Treatment at CTC" groups.

**Three new RDT cross-tabs** (after existing effective-abx cross-tabs):
- `crosstab-rdt-o1-anyabx-f1` — any antibiotic before admission vs discharge RDT
- `crosstab-rdt-o1-anyabx-f2` — any antibiotic at CTC vs discharge RDT
- `crosstab-rdt-o1-ineff-f2` — ineffective antibiotic at CTC vs discharge RDT (negative control)

**New "Antibiotic use overview" section**:
- `fig-abx-overview` — horizontal bar chart of % Yes for all six antibiotic categories (any/effective/ineffective × f1/f2), colour-coded by timing
- `crosstab-abx-categories-f1` — effective vs. ineffective before admission (overlap/collinearity check)
- `crosstab-abx-categories-f2` — effective vs. ineffective at CTC

### Vault

- Retired fleeting note [[ringer-vs-dehydration-covariate]] — idea implemented as Models 3g/h/i.

## Decisions made

- `t_admit_discharge` cannot be used as a covariate in `Surv(t_admit_discharge, rdt_cleared)` — it is the survival time axis and its inclusion would be circular/endogenous.
- `ringer_bin` replaces `dehydration` in the sensitivity series (3g/h/i); 3e retains both to demonstrate collinearity.
- `bold_p()` is not safe to use on `tbl_merge()` output in gtsummary; use `modify_table_styling()` per `p.value_*` column instead.

## Pending / open questions

(Carried forward)

- `temp_clean_discharge()` commented out — patches for C-12575, C-12557, C-24384 not applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose.
- `ors_f2` factor levels not yet confirmed.
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions.

## Files changed

- `R/4_data_exploration.qmd` — Model 3 Ringer series (3g/h/i), bold_p fix, descriptive stats expansion
