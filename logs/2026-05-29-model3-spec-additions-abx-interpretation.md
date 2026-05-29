---
title: "2026-05-29 Model 3 spec additions, antibiotic data flag, results interpretation"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-29"
updated: "2026-05-29"
type: session-log
project: uvira-sandbox
---

# 2026-05-29 — Model 3 spec additions, antibiotic data flag, results interpretation

## What was done

### Model 3 baseline changes

- **`a2` added** — `age_bin_f1 + sex_f1 + t_onset_admit`: demographic baseline with onset delay, sits between a1 and g.
- **`h` removed from baseline** — moved to archive under "Removed from baseline" comment. Archive's former `a2` (age_cat model) renamed to `a2c` to free the code.

### Model 3 active additions

| Code | Formula | Notes |
|------|---------|-------|
| `h2a` | `… + azith_f2` | h2v without doxy |
| `h2a0` | `… + azith_f2` (no Ringer) | h2a without severity proxy |
| `h2av` | `… + azith_f2 + vaccinated_23_f1` | primary (h2v) without doxy |

Models placed in order within the azith+doxy group in `model3_spec_active`.

### New fleeting notes

- [[antibiotic-data-paper-discrepancy]] — discrepancies between dataset and paper patient dossiers for antibiotic usage; unresolved; `cat_antibiotics_*` covariates flagged for caution.
- [[model3-results-interpretation-2026-05-29]] — in-progress interpretation of 29 May results (see below).

## Results interpretation (2026-05-29, in progress)

- **2023 vaccination** and **Ringer severity** both greatly reduce AIC.
- **Azith+doxy** has slightly lower AIC than any-effective (`cat_antibiotics_any_f2`); azithromycin HR is statistically significant in a single-covariate model.
- **Azith-only models have same fit as azith+doxy** — doxy term not contributing; consider dropping from primary line.
- **Outbreak context, doxy at CTC, pre-admission antibiotics** — weak or null effect on model fit.

## Decisions made

- None — doxy-removal from primary is an open question, not yet decided.

## Pending / open questions

- Resolve antibiotic data–paper discrepancy before interpreting antibiotic HRs (see [[antibiotic-data-paper-discrepancy]])
- Decide whether to drop doxy from primary model and promote an azith-only variant
- Run `diag-abx-freetext-unmatched` → revisit [[clean-antibiotics-ineffuvira-drift-risk]]
- Review zero-duration CTC stays (see [[calculate-event-intervals-zero-duration-review]])
- Implement `classify_serotype` discordance fix (see [[classify-serotype-dead-rules]])
- Verify `ind_register_2023_f1` values for `classify_vaccination` coverage

## Files changed

- `R/4_data_exploration.qmd` — model spec changes above

## Related

- [[survival-analysis-restructure-2026-05]]
- [[uvira-sandbox]]
