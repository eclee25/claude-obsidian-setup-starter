---
title: "Antibiotic data–paper discrepancy"
type: fleeting
created: "2026-05-29"
---

# Antibiotic data–paper discrepancy

Apparent discrepancies between antibiotic usage recorded in the dataset and what is documented in paper patient dossiers.

**Open question:** unclear whether the discrepancies reflect data entry errors, transcription gaps, differences in timing/classification, or something else. Need to investigate before placing further weight on antibiotic covariates in the survival models.

**To do:**
- Identify the extent and pattern of discrepancies (which antibiotics, which records, which direction)
- Determine source of truth (paper dossiers vs electronic entry)
- Decide whether to correct the data, flag affected records, or adjust modelling approach

**Impact:** affects `cat_antibiotics_*` covariates across all active Model 3 variants. See also [[clean-antibiotics-ineffuvira-drift-risk]] for a related code-level inconsistency risk.
