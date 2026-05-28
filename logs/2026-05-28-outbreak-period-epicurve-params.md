---
title: "2026-05-28 Outbreak period classification, epi curve, QMD parameters"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — Outbreak period classification, epi curve, QMD parameters

## What was done

### Survival analysis results promoted to permanent note

Promoted `fleeting/survival-results-interpretation-2026-05.md` to `permanent/survival-results-interpretation-2026-05.md` with substantially expanded content (time axis correction, univariate/multivariate findings, Ringer/severity hypothesis, antibiotic directionality hypotheses, open questions). Fleeting note archived. See [[survival-results-interpretation-2026-05]].

### `classify_serotype` dead rules flagged

`classify_serotype` (external repo) has two unreachable discordance rules in `cat_serotype`. Fix proposed, recorded in [[classify-serotype-dead-rules]] fleeting note. Not implemented — to be actioned in the relevant repository.

### `count_weekly_admissions()` added (`R/2_clinical_utils.R`)

Floors `dt_admission_f1` to Monday (`week_start = 1`), counts admitted patients per week, returns `week_start` / `n_weekly_admissions`. Called on the full `df_clinic` (before any row filtering) to ensure correct population-level weekly totals.

### `classify_outbreak_period()` added (`R/2_clinical_utils.R`)

Joins weekly counts to patient-level data by admission week. Adds `n_weekly_admissions` and one logical `outbreak_wkN` column per threshold value. Defaults: `thresholds = c(20, 30, 40)`. Thresholds are based on total weekly CTC admissions (Option A — single facility). Called at the end of the `df_clean` pipeline in `data-prep`.

### Weekly epi curve figure added (`R/4_data_exploration.qmd`)

New chunk `fig-epicurve` inserted in `## Descriptive` between `fig-ts` and `tab-descrip`. Uses `df_clean` (full cohort, not `df_analysis`). Stacked bar chart by admission week, stratified by `cat_rdt_o1_admit` (Positive/Negative/Invalid/Not tested). Three outbreak threshold lines at 20/30/40 cases/week with distinct linetypes (dotted/dashed/longdash), labelled at right edge with `annotate()`.

### `data_date` QMD parameter added (`R/4_data_exploration.qmd`)

New param `data_date: "2026_05_28"` controls:
- Input file names: `ECL_clinicalrdt_{data_date}.xlsx`, `ECL_antibiogram_{data_date}.xlsx`
- Export file name: `df_analysis_{data_date}.csv`

Render with new data pull:
```bash
quarto render R/4_data_exploration.qmd -P data_date:2026_06_04 -P require_culture:true
```

## Decisions made

- Outbreak period counts from `df_clinic` only (CTC, single facility) — not multi-facility historical data
- Week definition: Monday–Sunday (`week_start = 1`)
- Default thresholds: 20, 30, 40 cases/week

## Pending / open questions

(Carried forward)

- Implement `classify_serotype` discordance fix in the relevant repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` chunk and iterate on any remaining unmatched strings
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose — separate zero level?
- `temp_clean_discharge()` commented out — patches C-12575, C-12557, C-24384 intentionally skipped?
- `ors_f2` factor levels not yet confirmed

## Files changed

- `R/2_clinical_utils.R` — `count_weekly_admissions()`, `classify_outbreak_period()` added
- `R/4_data_exploration.qmd` — `fig-epicurve` chunk; `data_date` param; `df_weekly` + `classify_outbreak_period()` in `data-prep`; outbreak columns in select

## Related

- [[survival-results-interpretation-2026-05]] — promoted this session
- [[classify-serotype-dead-rules]] — fleeting note for external repo fix
- [[uvira-sandbox]] — project index
