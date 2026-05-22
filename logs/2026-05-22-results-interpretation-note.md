---
title: "2026-05-22 Survival analysis results interpretation note"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-22"
type: session-log
project: uvira-sandbox
---

# 2026-05-22 — Survival analysis results interpretation note

## What was done

### Results interpretation fleeting note created (`fleeting/survival-results-interpretation-2026-05.md`)

Added a fleeting note capturing the preliminary interpretation of the survival analysis results, intended to inform the discussion scheduled for next week. Contents:

- **Time axis correction**: previous analysis used symptom onset → discharge (flawed, as RDT status at onset is unknown); corrected to admission → discharge.
- **Univariate findings**: high Ringer volume and severe dehydration → HR < 1 (more severe patients less likely to be RDT− at discharge); `t_onset_admit` → HR > 1 (~26% higher probability RDT− per additional day delay).
- **Multivariate**: Ringer volume and `t_onset_admit` consistently significant across covariate combinations; dehydration less important after adjusting for demographics, further reduced when Ringer is added.
- **Antibiotic results**: none statistically significant; directionality — pre-admission Abx HR > 1, CTC Abx HR < 1. Two working hypotheses: (a) double-dosing for pre-admission patients; (b) confounding by indication for CTC recipients.

## Decisions made

None new (session was context restoration + save only).

## Pending / open questions

(Carried forward)

- `temp_clean_discharge()` commented out — patches for C-12575, C-12557, C-24384 not applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose.
- `ors_f2` factor levels not yet confirmed.
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions.
- Discuss results with Patrick next week.

## Files changed

- `fleeting/survival-results-interpretation-2026-05.md` — created
