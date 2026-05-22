---
title: "2026-05-22 Survival analysis restructure and antibiotic utility functions"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-22"
type: session-log
project: uvira-sandbox
---

# 2026-05-22 — Survival analysis restructure and antibiotic utility functions

## What was done

### New utility functions (`R/2_clinical_utils.R`)

- Added `clean_antibiotics_ineffUvira_f1()` — produces `cat_antibiotics_ineffUvira_f1`: antibiotic use prior to CTC admission that is NOT classified as effective in the Uvira population (complement of `cat_antibiotics_uvira_f1` from among all antibiotics). Inactive/marginal named cols: cefuroxime, flucloxacillin, metronidazole, penicillin.
- Added `clean_antibiotics_ineffUvira_f2()` — same logic for CTC-administered antibiotics (f2 form).
- Both called in the `df_clinic` pipeline in `R/4_data_exploration.qmd`.

### Survival analysis restructure (`R/4_data_exploration.qmd`)

**Time axis**: Changed from `t_onset_discharge` → `t_admit_discharge` throughout all survival models (Model 0, 1, 3). Rationale: `t_admit_discharge` directly measures the CTC stay duration; `t_onset_discharge` folded in pre-hospital delay which is not relevant to what happens during admission. See [[survival-analysis-restructure-2026-05]].

**`df_survival` prep**:
- Filter changed to `!is.na(t_admit_discharge)`
- Added `ors_f2` to `select()`
- Added explicit factoring for `cat_antibiotics_any_f2`, `cat_antibiotics_ineffUvira_f1`, `cat_antibiotics_ineffUvira_f2`

**Model 1 (univariate)**: Replaced 10 repetitive individual chunks with a loop-driven approach (`model1-spec` tibble + `purrr::map` fitting + `purrr::walk2` plotting). Added `cat_antibiotics_any_f2` (model j) and `cat_antibiotics_ineffUvira_f2` as null covariate (model k). 11 covariates total.

**Model 3 (multivariate)**: Replaced ad hoc Model 5 (7 models, some with collinearity issues) with a principled 6-model series:
- 3a: demographic baseline
- 3b: + severity at admission
- 3c: primary model (+ effective CTC antibiotics)
- 3d: + pre-admission antibiotics
- 3e: full with fluid resuscitation (exploratory; dehydration/ringer collinearity)
- 3f: sensitivity — any vs. effective antibiotics

Implemented as `results: asis` loop. Motivation text included under each model header in the rendered output. Retained interpretation bullets from Model 5 as reference.

**Stratification**: Agreed to defer stratification until `cox.zph()` flags a PH violation. Stratification on `cat_antibiotics_uvira_f2` was rejected because it is a primary exposure (not a nuisance confounder).

### Vault

- Created [[survival-analysis-restructure-2026-05]] — decision note documenting time axis choice, Model 1 covariate rationale, Model 3 series structure, and stratification policy.

## Decisions made

- `t_admit_discharge` replaces `t_onset_discharge` as survival time axis
- Stratification deferred; will use `tt()` for time-varying effect if PH violated for primary exposure
- `4_data_exploration_AbxF2Strat.qmd` is confirmed obsolete; only `4_data_exploration.qmd` is active

## Pending / open questions

- `temp_clean_discharge()` is commented out — manual patches for records C-12575, C-12557, C-24384 are not being applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose; may want a separate level for zero
- `ors_f2` structure not yet confirmed — factor levels unknown until data is inspected
- Run Model 1 and Model 3 fits to check `cox.zph()` outputs before finalising stratification decisions

## Files changed

- `R/2_clinical_utils.R` — new functions `clean_antibiotics_ineffUvira_f1`, `clean_antibiotics_ineffUvira_f2`
- `R/4_data_exploration.qmd` — pipeline, df_survival prep, Model 0/1/3 restructure
