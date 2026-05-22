---
title: "Survival analysis restructure: time axis, model set, and stratification rationale"
tags:
  - survival-analysis
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-22"
status: active
type: decision
project: uvira-sandbox
---

# Survival analysis restructure: time axis, model set, and stratification rationale

## Context

The discharge-RDT survival analysis in [[uvira-sandbox]] was initially built with `t_onset_discharge` (days from symptom onset to CTC discharge) as the survival time axis. During review, the model set (Model 5) was ad hoc and repetitive, and several structural choices were questioned: time axis, stratification usage, and covariate selection.

## Decision

Switch the survival time axis to `t_admit_discharge` (days from CTC admission to discharge), organise univariate models as a loop-driven Model 1 set, replace the exploratory Model 5 with a principled Model 3 multivariate series, and defer stratification until PH violations are confirmed.

## Alternatives considered

- **Keep `t_onset_discharge`** — rejected because it folds in the pre-hospital period (time from symptom onset to CTC admission), which is driven by health-seeking behaviour and geography rather than anything happening during the CTC stay. For a question about what predicts RDT clearance *during* hospitalisation, the relevant clock starts at admission.
- **Add `strata(cat_antibiotics_uvira_f2)` to multivariate models** — rejected because antibiotic use at the CTC is a primary exposure of scientific interest. Stratification absorbs the stratifying variable into the baseline hazard and produces no HR estimate. Stratification is appropriate only for nuisance confounders or when `cox.zph()` confirms a PH violation for that variable. See `R/4_data_exploration.qmd:1043`.

## Rationale

### Time axis

`t_admit_discharge` = duration of CTC stay. This directly measures how long the patient was observed and treated. Using `t_onset_discharge` would mix disease chronology with CTC stay length, biasing the time axis toward patients who presented late (who automatically have longer times regardless of what happened during admission).

### Model 1 — univariate covariates tested (`R/4_data_exploration.qmd:957`)

| Code | Variable | Rationale |
|------|----------|-----------|
| a | `age_bin_f1` | Primary demographic predictor |
| b | `sex_f1` | Demographic control |
| c | `ringer_bin` | IV fluid resuscitation at CTC |
| d | `ors_f2` | Oral rehydration at CTC |
| e | `dehydration` | Severity at admission |
| f | `t_onset_admit` | Pre-admission disease duration / health-seeking delay |
| g | `cat_antibiotics_uvira_f1` | Effective antibiotics before admission |
| h | `cat_antibiotics_uvira_f2` | Effective antibiotics at CTC — primary exposure |
| i | `cat_antibiotics_any_f1` | Any antibiotics before admission |
| j | `cat_antibiotics_any_f2` | Any antibiotics at CTC |
| k | `cat_antibiotics_ineffUvira_f2` | **Null covariate** (negative control) — antibiotics not expected to be effective; should show no signal |

### Model 3 — multivariate series (`R/4_data_exploration.qmd:1043`)

Each model builds on the previous to isolate specific contributions:

| Code | Label | Key addition | Purpose |
|------|-------|--------------|---------|
| 3a | Demographic baseline | `age_bin_f1 + sex_f1` | Demographic reference point |
| 3b | Severity at admission | `+ dehydration + t_onset_admit` | Pre-admission clinical picture |
| 3c | Primary | `+ cat_antibiotics_uvira_f2` | Main question: does effective CTC antibiotic predict clearance? |
| 3d | Pre-admission + CTC antibiotics | `+ cat_antibiotics_uvira_f1` | Controls for pre-admission antibiotic confounding |
| 3e | Full with fluids | `+ ringer_bin` | Exploratory — dehydration and ringer_bin are likely collinear; HR direction for dehydration expected to flip |
| 3f | Sensitivity | Replace uvira vars with `any` | Tests whether the signal is specific to the effectiveness classification |

### Stratification policy

Stratification will be added only if:
1. `cox.zph()` shows a significant Schoenfeld residual slope for a variable (PH violated), **and**
2. The variable is a nuisance confounder rather than a primary exposure.

If the PH assumption is violated for `cat_antibiotics_uvira_f2` specifically, a time-varying coefficient (`tt()`) is preferable to stratification, so the effect can still be quantified.

## Outcome

To be updated after first model fits on the full dataset.

## Related

- [[uvira-sandbox]] — project index
