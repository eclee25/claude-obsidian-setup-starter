---
title: "Model 3 results interpretation — 2026-05-29 (in progress)"
type: fleeting
created: "2026-05-29"
---

# Model 3 results interpretation — 2026-05-29 (in progress)

## Key findings

### Strong predictors
- **2023 vaccination** greatly reduces AIC — strong signal for vaccination as a predictor of RDT clearance.
- **Ringer lactate (severity proxy)** greatly reduces AIC relative to the demographic baseline (a1/a2) — severity at presentation is an important predictor.

### Antibiotic classification
- **Azithromycin and doxycycline** (individual CTC agents) have slightly lower AIC than the **any-effective-antibiotic** classification (`cat_antibiotics_any_f2`), suggesting the specific classification captures modest additional signal.
- **Azithromycin** has a statistically significant hazard ratio in a single-covariate model.
- **Azithromycin-only models (h2a, h2av) have the same fit as models including both azith and doxy** — doxycycline term does not improve fit; consider removing it from the active model line.

### Weak or null predictors
- **Outbreak context** (`outbreak_wk30`) — does not have a strong effect on model fit.
- **Doxycycline administration at CTC** — does not have a strong effect on model fit (consistent with azith-only finding above).
- **Pre-admission antibiotics** (`cat_antibiotics_uvira_f1`) — does not have a strong effect on model fit.

## Open questions / next steps
- Decide whether to drop doxycycline from the primary model line and promote an azith-only variant (h2av or h2a) as primary.
- Confirm whether the vaccination AIC reduction holds after stratification or subgroup checks.
