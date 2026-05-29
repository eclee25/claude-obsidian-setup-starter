---
title: "Review Model 3 primary model designation"
type: fleeting
created: "2026-05-29"
---

# Review Model 3 primary model designation

Currently `3h` ("Severity (Ringer) + CTC antibiotics") is designated as the primary model in `R/4_data_exploration.qmd` — it replaced `3c` when dehydration-based models were archived.

Review whether `3h` is the right choice or whether `3i` ("Ringer + pre-admission and CTC antibiotics") is more appropriate once Model 1 and Model 3 results are available.

Key considerations:
- Does adding `cat_antibiotics_uvira_f1` (pre-admission) materially change the CTC antibiotic HR?
- Is `3h` the most parsimonious model with adequate fit (check AIC and concordance from `tbl-model3-fit`)?
- Deviance residuals (`fig-deviance-resid-3h`) and Schoenfeld plots should inform whether `3h` satisfies PH and fits the data well before it is locked in as primary.

File: `R/4_data_exploration.qmd` — `model3-spec` chunk, `fig-deviance-resid-3h`, `fig-martingale-onset` subtitle.
