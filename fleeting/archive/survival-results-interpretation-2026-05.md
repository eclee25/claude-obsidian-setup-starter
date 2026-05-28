---
title: "Survival analysis: preliminary results interpretation"
tags:
  - uvira-sandbox
created: "2026-05-22"
type: fleeting
---

# Survival analysis: preliminary results interpretation

Revised analyses to discuss next week:

* Previous analysis was flawed: time axis was symptom onset → discharge even though RDT status at symptom onset is unknown. Fixed to admission → discharge.
* **Univariate**: high Ringer volume and severe dehydration had significant HRs < 1 relative to low-volume / mild categories (i.e. more severe patients less likely to be RDT- at discharge).
* **Univariate**: `t_onset_admit` had a significant HR > 1 — each additional day of delay from onset to admission associated with ~26% higher probability of being RDT- at discharge. Makes sense as it represents time passing over the disease course.
* **Multivariate**: Ringer volume and `t_onset_admit` are consistently significant with similar HRs to univariate across covariate combinations.
* **Interaction between Ringer, dehydration, and `t_onset_admit`**: adding Ringer to a model reduces the importance of `t_onset_admit`. Dehydration never reaches significance after adjusting for demographics, and becomes even less important when Ringer is included.
* **Antibiotics**: none statistically significant. Directionality: pre-admission Abx → HR > 1 (higher probability RDT- at discharge); CTC Abx → HR < 1 (lower probability). Near-universal CTC Abx use — non-administration may reflect stock-out or unusual circumstances rather than treatment decision.
* Comparing effective / ineffective / any Abx: magnitude of effects in expected order; effective Abx had narrower CIs. Directionality consistent: pre-admission HR > 1, CTC HR < 1, neither statistically significant.

## Interpretation

If Ringer is the best proxy for cholera severity (per Patrick): severe cases may be less likely to be RDT- at discharge because severe cholera is usually discharged 6–12h after diarrhea stops while mild cases may have had lower shedding from the start. The dose-response in moderate vs. high Ringer volume groups may reinforce this.

Abx results are puzzling — hypotheses:

* Pre-admission Abx patients may be receiving 2× antibiotics (most also receive CTC Abx), which could explain higher probability of RDT- at discharge — but directionality holds even after adjusting for CTC Abx use (though neither is significant so caution warranted).
* Odd that CTC Abx recipients are less likely to be RDT- at discharge — likely confounding by indication (sicker patients more likely to receive Abx and less likely to clear). Do not overinterpret while HR CI crosses 1.
