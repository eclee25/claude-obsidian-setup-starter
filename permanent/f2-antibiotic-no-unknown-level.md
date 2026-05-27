---
title: "F2 antibiotic functions: no Unknown level"
tags:
  - uvira-sandbox
created: "2026-05-27"
updated: "2026-05-27"
status: active
type: decision
project: uvira-sandbox
---

# F2 antibiotic functions: no Unknown level

## Context

The f1 antibiotic cleaning functions (`clean_antibiotics_any_f1`, `clean_antibiotics_gtfcc_f1`, `clean_antibiotics_uvira_f1`) include an `uncertain_pattern` that classifies vague free-text entries in `medicines_other_f1` as `"Unknown"` (e.g. "autre médicament", "nature non connue", "antibiotiques non connus"). This reflects that patients may not know or correctly recall what they took before arriving at the CTC.

During the f1/f2 pattern overhaul (see session log [[2026-05-27-azith-doxy-functions-freetext-patterns]]), the question arose whether to add an equivalent `"Unknown"` level to the f2 functions (`clean_antibiotics_any_f2`, `clean_antibiotics_gtfcc_f2`, `clean_antibiotics_uvira_f2`), which are currently binary Yes/No. The f2 field `antibiotic_name_other_f2` captures antibiotics administered during the CTC stay.

## Decision

Do not add an `"Unknown"` level to the f2 antibiotic functions. All f2 functions remain binary Yes/No (`R/2_clinical_utils.R:396`, `R/2_clinical_utils.R:459`, `R/2_clinical_utils.R:523`).

## Alternatives considered

- **Add Unknown level to f2** — rejected. Antibiotics administered at the CTC are prescribed and dispensed by clinical staff and recorded in the CTC register. Unlike pre-admission medications reported by patients, CTC medications should always be identifiable. An "Unknown" entry in `antibiotic_name_other_f2` most likely reflects a data entry error or a drug already captured by a checkbox, not genuine uncertainty.

## Rationale

The asymmetry between f1 and f2 is clinically motivated: f1 captures patient-reported recall of community medications (high uncertainty, vague entries expected), while f2 captures CTC staff-recorded treatments (documentation expected to be complete). A free-text entry in f2 that cannot be matched to a known antibiotic is more informative as `"No"` (not a recognised antibiotic) than as `"Unknown"` (could not determine).

## Outcome

To be updated after running the diagnostic chunk (`diag-abx-freetext-unmatched`) — if a meaningful volume of legitimate-but-unclassifiable antibiotic names appear in f2, this decision can be revisited.

## Related

- [[survival-analysis-restructure-2026-05]] — model covariate context for these variables
- [[uvira-sandbox]] — project index
