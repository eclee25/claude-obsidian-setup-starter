---
title: "Survival analysis results: model selection interpretation (29 May 2026)"
tags:
  - uvira-sandbox
created: "2026-05-29"
updated: "2026-05-29"
status: active
type: concept
project: uvira-sandbox
---

# Survival analysis results: model selection interpretation (29 May 2026)

In-progress interpretation of model selection results from the restructured Model 3 suite (baseline, active, null, archive sections). Outcome: time from CTC admission to RDT-negative discharge.

## Findings

### Ringer vs demographic baseline (AIC)

Ringer's lactate volume (`ringer_bin`) substantially reduces AIC relative to the demographic baseline (3a1). This confirms that admission severity — as proxied by Ringer's volume administered — is an important predictor of RDT clearance by discharge and should be retained in all active models.

### 2023 vaccination (AIC)

Adding `vaccinated_23_f1` to models greatly reduces AIC. This is a notably strong effect on model fit and suggests that vaccination status is an important predictor of RDT clearance at discharge, independently of antibiotic use and severity. The mechanistic interpretation is unclear at this stage — possibilities include: (1) vaccination-induced partial immunity shortens the duration of shedding; (2) vaccinated patients differ systematically from unvaccinated patients on unmeasured characteristics correlated with faster clearance.

### Azithromycin and doxycycline vs uvira effective classification (AIC + Model 1)

Using individual CTC agent variables (`cat_antibiotics_azith_f2`, `cat_antibiotics_doxy_f2`) instead of the aggregate uvira-effective classification (`cat_antibiotics_uvira_f2`) produces slightly lower AIC.

In Model 1 (univariate), **azithromycin administration** (`cat_antibiotics_azith_f2`) comes out as statistically significant. Doxycycline did not reach significance in the univariate analysis.

This suggests that the specific CTC antibiotic administered matters beyond whether an effective antibiotic was given, and that azithromycin in particular may have a detectable association with RDT clearance. Caution warranted: (1) azithromycin and doxycycline are highly correlated with each other in this cohort (most patients who receive one receive the other — see `tab-azith-doxy-coadmin`); (2) near-universal CTC antibiotic administration creates confounding by indication (sicker patients → more likely to receive antibiotics and less likely to clear).

### Outbreak context and pre-admission antibiotics (AIC)

Neither `outbreak_wk30` nor `cat_antibiotics_uvira_f1` (pre-admission effective antibiotics) has a strong effect on model fit. These covariates were archived (hk, ik, h2k) or removed from the active analysis line given their limited contribution to AIC reduction.

## Open questions

- Is the vaccination effect on AIC driven by a true biological effect or by selection bias (vaccinated patients seeking care earlier, being healthier, or living in areas with better access)?
- Multicollinearity between `vaccinated_23_f1` and `t_onset_admit` to be assessed — see `fig-collin-vacc-onset` and `tab-collin-vacc-onset`.
- Are azithromycin and doxycycline too collinear in this dataset to estimate independent effects? Check `tab-azith-doxy-coadmin` and VIF once models are fit.
- Model fit statistics (AIC, concordance) not yet numerically extracted — interpretation above is qualitative pending rendered output.

## Related

- [[survival-results-interpretation-2026-05]] — earlier interpretation (univariate findings, Ringer/severity hypothesis, antibiotic directionality)
- [[survival-analysis-restructure-2026-05]] — time axis decisions, Model 1/3 covariate structure
- [[uvira-sandbox]] — project index
