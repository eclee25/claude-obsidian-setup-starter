---
title: "2026-05-29 Model 3 restructure, new active models, data quality checks"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-29"
updated: "2026-05-29"
type: session-log
project: uvira-sandbox
---

# 2026-05-29 — Model 3 restructure, new active models, data quality checks

## What was done

### `tab-descrip` — `cat_culture` added

`cat_culture` added to `include`, label ("Culture result at admission"), `fisher.test`, and Status at admission row group.

### Data quality — under-5 doxycycline table

New section added before `# Export`:

- `tab-doxy-underage-summary` — count of under-5 + doxycycline records by year (with Total row)
- `tab-doxy-underage` — full record-level table (record_id, age, age_bin, doxy flag, admission date)

Filter: `age_bin_f1 == "1-4 years"` (confirmed level name from `get_age_cat`).

### Model 3 split into Active / Archive / Null sections

`model3_spec` replaced by three tibbles:

- `model3_spec_active` — Ringer-based severity, no dehydration/age_cat_f1/any_f2
- `model3_spec_archive` — dehydration or age_cat_f1 models (a2, b, c, d, e, j1, j2, k, l)
- `model3_spec_null` — model f with cat_antibiotics_any_f1; cat_antibiotics_any_f2 removed

Combined as `model3_spec_all` for fitting; split back into `fits3_active`, `fits3_archive`, `fits3_null`.

Each section has its own loop (`fig-model3-active/archive/null`), fit statistics table, and Schoenfeld plots. Archive and Null use separate heading levels (`## Model 3 — Archive`, `## Model 3 — Null`).

### Model 3 diagnostics (from prior session, now active-only)

- `tbl-model3-fit` — active models only; references `fits3_all[["fit3a1"]]` as baseline
- `fig-schoenfeld-active` / `fig-schoenfeld-archive` — separate PH residual plots per section
- `fig-deviance-resid-3i` — deviance residuals for primary model 3i (was 3c, then 3h)
- `fig-martingale-onset` — base model updated to 3i structure (minus t_onset_admit): `age_bin_f1 + sex_f1 + ringer_bin + cat_antibiotics_uvira_f1 + cat_antibiotics_uvira_f2`

Bug fixed: `tibble()` size mismatch in deviance residual chunk — `df_survival$record_id` (308 rows) vs `residuals()` (284 rows, complete cases only). Fixed with `setdiff(seq_len(nrow(df_survival)), as.integer(fit$na.action))` to subset correctly.

### Overview table at start of Model 3

`tbl-model3-overview` renders `model3_spec_active` as a table of codes, formulas, and motivations at the top of the section.

### Model 3 active models expanded — 14 total

Primary model: **3i** (Ringer + pre-admission + CTC uvira antibiotics).

| Group | Codes |
|---|---|
| Baselines | a1, g |
| Uvira effective — primary line | h, i (primary), iv, ik, ivk |
| Uvira effective — CTC only | hv, hk, hvk |
| Azith + doxy | h2, h2v, h2k, h2vk |

Vaccination (`vaccinated_23_f1`) and outbreak (`outbreak_wk30`) added in all combinations to both antibiotic groups. No individual azith-only or doxy-only models.

### Fleeting note archived

`model3-primary-designation-review.md` → `fleeting/archive/` (primary designated as 3i).

## Decisions made

- Primary model: 3i (`age_bin_f1 + sex_f1 + ringer_bin + t_onset_admit + cat_antibiotics_uvira_f1 + cat_antibiotics_uvira_f2`)
- Two antibiotic groups for contextual model extensions: uvira effective classification vs azith + doxy together
- No individual azith-only or doxy-only active models
- `cat_antibiotics_any_f2` removed from all active models
- Archive criterion: dehydration or age_cat_f1 covariate present

## Pending / open questions

(Carried forward)

- **`tbl-model3-summary` may be very wide** with 14 active models — consider splitting into uvira group / azith+doxy group when rendering
- Implement `classify_serotype` discordance fix in external repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` → revisit [[clean-antibiotics-ineffuvira-drift-risk]]
- Review zero-duration CTC stays (see [[calculate-event-intervals-zero-duration-review]])
- Verify `ind_register_2023_f1` values to check `classify_vaccination` coverage

## Files changed

- `R/4_data_exploration.qmd` — all changes above

## Related

- [[calculate-event-intervals-zero-duration-review]] — outstanding fleeting note
- [[clean-antibiotics-ineffuvira-drift-risk]] — outstanding fleeting note
- [[classify-serotype-dead-rules]] — outstanding fleeting note
- [[uvira-sandbox]] — project index
