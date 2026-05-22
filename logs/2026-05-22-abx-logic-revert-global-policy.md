---
title: "2026-05-22 Antibiotic logic revert and global code change policy"
tags:
  - session-log
  - uvira-sandbox
  - meta
created: "2026-05-22"
updated: "2026-05-22"
type: session-log
project: uvira-sandbox
---

# 2026-05-22 — Antibiotic logic revert and global code change policy

## What was done

### `clean_antibiotics_ineffUvira_f1/f2` — reverted, comments added (`R/2_clinical_utils.R`)

A previous incorrect change made both `ineffUvira` functions derive their output as the complement of `uvira` within `any` (i.e. `any == "Yes" & uvira != "Yes"`). This was reverted to the original pattern-based logic (specific checkboxes + named free-text patterns for known-ineffective drugs).

**Reason for revert**: the complement definition conflates "known ineffective" with "unknown/uncertain effectiveness". The gap between `any` and `(effective + ineffective)` is intentional — it represents patients whose antibiotic identity was ambiguous (e.g. "autres antibiotiques", "médicament non connu"). The three categories are conservative and independent, not exhaustive partitions.

**What was added**: an explanatory comment in both functions (`R/2_clinical_utils.R:317` and `R/2_clinical_utils.R:548`) noting that the gap is intentional and what it represents.

### Global code change policy added (`~/vault/CLAUDE.md`)

Added a "Code Change Policy" section to the global `CLAUDE.md` (applied across all projects):

- **Code changes** (implement directly): refactoring, syntax, renaming, performance, rendering bugs, test fixes.
- **Domain/content logic changes** (describe options first, implement only after approval): variable definitions, classification rules, inclusion/exclusion criteria, clinical thresholds, covariate definitions, handling of uncertain/unknown cases.
- When in doubt, treat as domain logic and ask first.

## Decisions made

- `ineffUvira` categories are deliberately conservative: they identify *known* ineffective drugs, not everything outside the effective list. The gap to `any` is a feature, not a bug.
- Domain/content logic changes require explicit approval before implementation, across all projects.

## Pending / open questions

(Carried forward from prior sessions)

- `temp_clean_discharge()` commented out — patches for C-12575, C-12557, C-24384 not applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose.
- `ors_f2` factor levels not yet confirmed.
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs.

## Files changed

- `R/2_clinical_utils.R` — reverted `ineffUvira_f1/f2`, added explanatory comments
- `~/vault/CLAUDE.md` — global code change policy
