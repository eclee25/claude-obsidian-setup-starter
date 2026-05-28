---
title: "clean_antibiotics_ineffUvira drift risk"
type: fleeting
created: "2026-05-28"
---

# clean_antibiotics_ineffUvira drift risk

`clean_antibiotics_ineffUvira_f1` and `clean_antibiotics_ineffUvira_f2` each duplicate:
- the `uvira_cols` vector (used to derive `ineff_uvira_cols` via `setdiff`)
- the `ineff_uvira_other_pattern` free text regex (mirrors `non_uvira_pattern` in `clean_antibiotics_uvira_*`)

These are currently in sync with `clean_antibiotics_uvira_f1` and `clean_antibiotics_uvira_f2` as of 2026-05-28. But they are defined twice — once per function pair — with no shared constant.

**Risk:** any future edit to the effective drug list or free text patterns in `clean_antibiotics_uvira_*` must be manually mirrored in the corresponding `ineffUvira_*` function or the two classifications will silently diverge.

**When to act:** after the `diag-abx-freetext-unmatched` iteration is complete and the patterns are stable. Refactor options: (1) extract shared constants to the top of the antibiotic section; (2) have `ineffUvira` call into `uvira` internals.

File: `R/2_clinical_utils.R`
