---
title: "2026-05-28 cox.zph crash fix"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — cox.zph crash fix

## What was done

### `cox.zph()` wrapped in `tryCatch()` (`R/4_data_exploration.qmd`)

Both `fig-model1-all` and `fig-model3-all` loops were crashing at `fit1p3` (`vaccinated_25_f1`). Root cause: the 2025 vaccination campaign has near-zero vaccinated patients in the analysis cohort, so `coxph()` fits a degenerate model with an `NA` coefficient and `cox.zph()` cannot compute Schoenfeld residuals (`subscript out of bounds`).

Fix: wrapped `cox.zph(fit)` in `tryCatch()` in both loops. Failed models print a labelled message and the loop continues.

`vaccinated_25_f1` is a candidate for removal from `model1-spec` given the data sparsity — to assess after reviewing rendered output.

## Pending / open questions

(Carried forward)

- **Review survival model changes** from prior session before running final analysis
- `vaccinated_25_f1` likely too sparse for Model 1 — consider dropping after reviewing output
- Implement `classify_serotype` discordance fix in external repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` chunk → then revisit [[clean-antibiotics-ineffuvira-drift-risk]]
- Review zero-duration CTC stays (see [[calculate-event-intervals-zero-duration-review]])
- `ringer_bin` lowest bin conflates zero Ringer's with low-dose
- `temp_clean_discharge()` commented out — intentional?
- Verify `ind_register_2023_f1` values to check `classify_vaccination` coverage

## Files changed

- `R/4_data_exploration.qmd` — `tryCatch()` around `cox.zph()` in `fig-model1-all` and `fig-model3-all`

## Related

- [[uvira-sandbox]] — project index
