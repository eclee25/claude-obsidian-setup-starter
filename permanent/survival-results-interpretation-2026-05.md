---
title: "Survival analysis results: interpretation (May 2026)"
tags:
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-28"
status: active
type: concept
project: uvira-sandbox
---

# Survival analysis results: interpretation (May 2026)

Preliminary interpretation of the Cox proportional hazards survival analysis for RDT shedding at discharge. Outcome: time from admission to RDT-negative discharge among RDT-positive CTC admissions.

## Time axis correction

Previous analysis was flawed: the time axis ran from symptom onset to discharge, but RDT status at symptom onset is unknown. Corrected to admission → discharge.

## Findings

### Univariate

- **Ringer volume**: high volume had a significant HR < 1 relative to the low-volume category — more severe patients (as proxied by IV fluid requirement) are less likely to be RDT-negative at discharge.
- **Dehydration**: severe dehydration had a significant HR < 1 relative to mild. Directionally consistent with Ringer volume.
- **`t_onset_admit`**: significant HR > 1 — each additional day of delay from symptom onset to CTC admission is associated with approximately a 26% higher probability of being RDT-negative at discharge. Interpretable as time passing over the natural disease course.
- **Antibiotics** (all types): none statistically significant in univariate analyses.

### Multivariate

- Ringer volume and `t_onset_admit` are consistently significant with similar HRs to univariate models across different covariate combinations.
- **Interaction between Ringer, dehydration, and `t_onset_admit`**: adding Ringer to a model reduces the apparent importance of `t_onset_admit`. Dehydration never reaches significance after adjusting for demographic factors, and becomes even less important when Ringer is added.
- None of the antibiotic covariates reach statistical significance. Comparing effective (in Uvira) / ineffective / any Abx: effect magnitudes are in the expected order; use of antibiotics effective in Uvira had narrower confidence intervals than other types.

### Antibiotic directionality

Pre-admission Abx use: HR > 1 (higher probability of being RDT-negative at discharge).
CTC Abx use: HR < 1 (lower probability of being RDT-negative at discharge).

The vast majority of patients receive antibiotics in the CTC; non-administration likely reflects stock-out or unusual circumstances rather than a treatment decision. This makes interpretation of CTC Abx effects difficult.

## Interpretation

### Ringer / severity

If Ringer volume is the best available proxy for cholera severity (informed by discussion with Patrick): severe cases may be less likely to be RDT-negative at discharge because severe cholera is typically discharged 6–12 hours after watery diarrhea stops, while mild cases may have had lower shedding from the start. The apparent dose-response across low / moderate / high Ringer volume categories may reinforce this reading.

### Antibiotic results

The antibiotic findings are puzzling, particularly the opposite directionality for pre-admission vs CTC use. Working hypotheses:

1. **Double-dosing**: pre-admission Abx patients likely also receive CTC Abx, effectively receiving two courses. This could explain the HR > 1 for pre-admission use, though the directionality holds even after adjusting for CTC Abx use (with neither reaching significance — caution warranted against overinterpretation).
2. **Confounding by indication for CTC Abx**: sicker patients are more likely to receive antibiotics in the CTC and less likely to clear RDT positivity. The HR < 1 for CTC Abx use may reflect this confounding rather than a true negative effect of treatment. Do not overinterpret while the HR confidence interval crosses 1.

## Open questions

- Neither pre-admission nor CTC Abx results are statistically significant — are the models adequately powered for these covariates given near-universal CTC Abx administration?
- Should CTC Abx use be modelled differently given the near-universal uptake (e.g., time-to-first-dose, or restricted to the subgroup that did not receive Abx)?
- Is the `t_onset_admit` × Ringer interaction worth modelling explicitly?

## Related

- [[survival-analysis-restructure-2026-05]] — time axis decisions, Model 1/3 covariate structure, stratification policy
- [[uvira-sandbox]] — project index
