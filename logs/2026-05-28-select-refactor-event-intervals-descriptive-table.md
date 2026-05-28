---
title: "2026-05-28 Select refactor, calculate_event_intervals, descriptive table update"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — Select refactor, calculate_event_intervals, descriptive table update

## What was done

### `df_analysis` select block tightened (`R/4_data_exploration.qmd`)

Replaced broad `contains("f2")`, `contains("f3")`, `contains("cat_antibiotics")` with explicit column lists organised into labelled sections. Removed unused columns (`consent_f1`, `tm_onset_symptoms_f1`, `dttm_onset_diarrhea_f1`, `n_hh_members_f1`, `pregnant_f1`, `medication_use_f1`, `contains("medicines_f1")`). Added fallback date/datetime columns needed by `calculate_event_intervals()`: `dttm_onset_diarrhea_f1`, `dt_outcome_f2`.

### `calculate_event_intervals()` added (`R/2_clinical_utils.R`)

Extracted the two inline `mutate` blocks from `data-prep` into a new utility function. Key design decisions (confirmed by user):

- **Onset source:** `coalesce(as.Date(dttm_onset_diarrhea_f1), as.Date(dt_onset_symptoms_f1))` — prefers diarrhea datetime, falls back to symptom onset date
- **Outcome source:** `coalesce(as.Date(dttm_outcome_f2), as.Date(dt_outcome_f2))` — prefers outcome datetime, falls back to date
- **Precision:** whole-day date arithmetic (`as.numeric(date2 - date1)`) — appropriate for daily-interval survival analysis; same-day admission/discharge correctly codes as `t_admit_discharge = 0`
- **Negative guard:** both mutate blocks retained internally; negative intervals set to `NA`

Intermediates `.date_onset` / `.date_outcome` created within the function and dropped with `select(-c(...))`.

### `calculate_durations()` deleted (`R/2_clinical_utils.R`)

Confirmed no downstream variables (`duration_hosp`, `cat_duration_hosp`, `home_delay`, `cat_home_delay`, `date_outcome`, `date_onset_symptoms`) were referenced anywhere. Functionality subsumed by `calculate_event_intervals()` with better column resolution logic. Call removed from `4_data_exploration.qmd` and `4_data_exploration_AbxF2Strat.qmd`.

### `convert_to_date()` call trimmed (`R/4_data_exploration.qmd`)

Removed `dttm_outcome_f2`, `swab_datetime_f3`, `swab_datetime_f3b` from the `cols` argument — these are datetime columns handled by `calculate_event_intervals()` internally. Keeping them in `convert_to_date()` was redundant and conceptually wrong (strips time before the function designed to handle them). Retained: `dt_onset_symptoms_f1`, `dt_admission_f1`, `dt_interview_f1` (date columns that need normalisation from Excel POSIXct imports).

### `tab-descrip` updated with all potential covariates (`R/4_data_exploration.qmd`)

New variables added:

| Variable | Section | Test |
|---|---|---|
| `cat_serotype` | Status at admission | `fisher.test` |
| `ors_f2` | Treatment at CTC | `wilcox.test` (numeric: number of gobelets; high missingness) |
| `cat_antibiotics_azith_f2` | Treatment at CTC | `fisher.test` |
| `cat_antibiotics_doxy_f2` | Treatment at CTC | `fisher.test` |
| Vaccination (5 vars) | New **Vaccination** section | `fisher.test` |
| `n_weekly_admissions` | New **Admission context** section | `wilcox.test` |
| `outbreak_wk20/30/40` | New **Admission context** section | `chisq.test` |

Antibiotic footnote updated to describe all four groupings (any, effective Uvira, ineffective Uvira, individual agents). Typos fixed: `azithryomycin` → `azithromycin`, `gentamyycin` → `gentamycin`.

### `clean_antibiotics_ineffUvira` drift risk noted

Confirmed that `ineff_uvira_other_pattern` in `ineffUvira_f1/f2` currently matches `non_uvira_pattern` in `uvira_f1/f2`, and `uvira_cols` vectors are identical. No immediate update needed. Risk: duplicated definitions will silently drift if uvira functions are updated without mirroring. See [[clean-antibiotics-ineffuvira-drift-risk]].

## Decisions made

- Whole-day precision for `t_*` variables is correct for daily-interval survival analysis
- Same-day admission/discharge → `t_admit_discharge = 0` is the correct coding
- `ors_f2` treated as continuous (number of gobelets); high missingness will display via `missing = "ifany"`
- Datetime columns should not be pre-converted to Date before `calculate_event_intervals()`

## Pending / open questions

(Carried forward)

- Implement `classify_serotype` discordance fix in the relevant repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` chunk and iterate on any remaining unmatched strings — **then** revisit [[clean-antibiotics-ineffuvira-drift-risk]] refactor
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose — separate zero level?
- `temp_clean_discharge()` commented out — patches C-12575, C-12557, C-24384 intentionally skipped?
- `ors_f2` factor levels not yet confirmed (now confirmed numeric — number of gobelets)
- Verify `ind_register_2023_f1` values to check `classify_vaccination` coverage
- `tab-vaccination` section in QMD is now redundant with the updated `tab-descrip` — remove?

## Files changed

- `R/2_clinical_utils.R` — `calculate_durations()` deleted; `calculate_event_intervals()` added (renamed from `calculate_survival_times()`)
- `R/4_data_exploration.qmd` — select block tightened; `convert_to_date()` trimmed; `calculate_event_intervals()` call; `tab-descrip` expanded; antibiotic footnote updated
- `R/4_data_exploration_AbxF2Strat.qmd` — `calculate_durations()` call removed

## Related

- [[clean-antibiotics-ineffuvira-drift-risk]] — fleeting note created this session
- [[survival-results-interpretation-2026-05]] — permanent note
- [[uvira-sandbox]] — project index
