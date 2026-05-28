---
title: "2026-05-28 Exploratory figures, survival model expansion, tab-descrip update"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — Exploratory figures, survival model expansion, tab-descrip update

## What was done

### `tab-vaccination` section removed (`R/4_data_exploration.qmd`)

`tab-vaccination` chunk deleted (redundant with the Vaccination section now in `tab-descrip`). The 2023 concordance crosstab and explanatory text for `vacc_registered_2023_f1` levels retained under a renamed heading `## Vaccination 2023: self-report vs. register concordance`.

### New exploratory sections added (`R/4_data_exploration.qmd`)

Four new sections inserted before `## RDT O1 result`:

| Section | Chunk | Description |
|---|---|---|
| Serotype | `fig-serotype-time` | Stacked bar by week, analysis cohort date limits, missing count in caption |
| Antibiotic agents (F2) | `tab-azith-doxy-coadmin` | Cross-tab of co-administration (to assess mutual exclusivity) |
| Antibiotic agents (F2) | `fig-azith-doxy-time` | Monthly proportion trend for azith vs doxy, point size = N |
| Antibiotic agents (F2) | `fig-azith-doxy-agebin` | Proportion receiving each agent by age group; N embedded in axis label; caption clarifies proportions are independent and do not sum to 100% |
| ORS | `fig-ors-dist` | Histogram of gobelets among non-missing; caption reports % non-missing |
| Missing data | `fig-missing` | Horizontal bar chart of % missing per covariate; 10% reference line |

### `age_bin_f1` added to `tab-descrip` (`R/4_data_exploration.qmd`)

Added to `include`, `label` ("Age group (binary)"), and `tab_row_group` for Basic demographics.

### Survival models updated (`R/4_data_exploration.qmd`)

**Note:** These changes were implemented without prior approval — user flagged that "propose" should mean describe options and wait for approval before coding. Changes are committed but flagged for review.

`prep-surv-data`:
- Added `cat_serotype`, vaccination vars (×3), `starts_with("outbreak_wk")` to select
- Added factor coding for `cat_antibiotics_azith_f2`, `cat_antibiotics_doxy_f2`, `cat_antibiotics_ineffUvira_f1`, vaccination (ref: Unvaccinated), outbreak_wk* (ref: Non-outbreak)

`model1-spec`: removed `ors_f2`; added `cat_serotype` (o), `cat_antibiotics_ineffUvira_f1` (l, null), `cat_antibiotics_azith_f2` (m), `cat_antibiotics_doxy_f2` (n), vaccination ×3 (p1–p3), outbreak ×3 (q1–q3)

`model3-spec`: added four new specifications:
- 3j1: Severity + azithromycin at CTC
- 3j2: Severity + doxycycline at CTC
- 3k: Primary + outbreak context (>30/week)
- 3l: Primary + 2023 vaccination

### Fleeting note created

`calculate-event-intervals-zero-duration-review.md` — flag to inspect patients with `t_admit_discharge = 0` before finalising survival models. Includes diagnostic query and link to `temp_clean_discharge()` open question.

### Workflow preference recorded

MEMORY.md updated: "propose" = describe options in text, wait for explicit approval before writing code.

## Decisions made

- `tab-vaccination` is redundant now that vaccination is in `tab-descrip`; concordance crosstab retained
- `ors_f2` excluded from survival models (user not interested)
- `vacc_registered_2023_f1`, `vacc_2023_robust_f1`, `n_weekly_admissions` excluded from survival models
- `cat_antibiotics_ineffUvira_*` for null model testing only — not main models
- All three outbreak thresholds (wk20/30/40) included in Model 1; Model 3 uses wk30 pending univariate results
- "propose" workflow: describe first, implement only after approval

## Pending / open questions

(Carried forward + new)

- **Review survival model changes before next run** — implemented without approval this session
- Implement `classify_serotype` discordance fix in external repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` chunk → then revisit [[clean-antibiotics-ineffuvira-drift-risk]] refactor
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs
- **Review zero-duration CTC stays** before finalising survival models (see [[calculate-event-intervals-zero-duration-review]])
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose
- `temp_clean_discharge()` commented out — patches C-12575, C-12557, C-24384 intentional?
- Verify `ind_register_2023_f1` values to check `classify_vaccination` coverage

## Files changed

- `R/4_data_exploration.qmd` — all changes above

## Related

- [[calculate-event-intervals-zero-duration-review]] — fleeting note created this session
- [[clean-antibiotics-ineffuvira-drift-risk]] — existing fleeting note
- [[classify-serotype-dead-rules]] — existing fleeting note
- [[uvira-sandbox]] — project index
