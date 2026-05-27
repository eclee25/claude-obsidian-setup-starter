---
title: "2026-05-27 Vaccination descriptive statistics"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-27"
updated: "2026-05-27"
type: session-log
project: uvira-sandbox
---

# 2026-05-27 — Vaccination descriptive statistics

## What was done

### Vaccination descriptive section added (`R/4_data_exploration.qmd`)

Inserted a new `## Vaccination status` section between the `tab-descrip` chunk and `## RDT O1 result: admission vs. discharge`.

**Chunk `tab-vaccination`** — `tbl_summary` table with all 5 vaccination variables, stratified by discharge RDT result. Matches existing `tab-descrip` style: overall column, RDT-stratified columns, N headers, bold labels, `missing = "ifany"`.

Variables included:

| Variable | Description |
|---------|-------------|
| `vaccinated_20_f1` | Vaccinated 2020 campaign (self-report only) |
| `vaccinated_23_f1` | Vaccinated 2023 campaign (self-report only) |
| `vaccinated_25_f1` | Vaccinated 2025 campaign (self-report only) |
| `vacc_registered_2023_f1` | 2023 status — 4-level concordance (self-report × register) |
| `vacc_2023_robust_f1` | Robust 2023 definition — vaccinated AND in register (binary, NA for discordant) |

**Chunk `crosstab-vacc-2023`** — `tabyl` cross-tab of `vaccinated_23_f1 × vacc_registered_2023_f1`, with row/column totals, percentages, and counts. Makes the concordance/discordance pattern explicit.

`vacc_registered_2023_f1` level ordering in cross-tab: `confirmed_vaccinated` → `unconfirmed_vaccinated` → `unvaccinated_registered` → `confirmed_unvaccinated`.

Inline note under `tab-vaccination` explains the four `vacc_registered_2023_f1` levels and flags that `vacc_2023_robust_f1` is `NA` for the two discordant groups.

## Decisions made

None new this session. See [[f2-antibiotic-no-unknown-level]] (prior session).

## Pending / open questions

(Carried forward)

- Run `diag-abx-freetext-unmatched` chunk and iterate on any remaining unmatched strings
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose — separate zero level?
- `temp_clean_discharge()` commented out — patches C-12575, C-12557, C-24384 intentionally skipped?
- `ors_f2` factor levels not yet confirmed

## Files changed

- `R/4_data_exploration.qmd` — vaccination section added (chunks `tab-vaccination`, `crosstab-vacc-2023`)

## Related

- [[2026-05-27-azith-doxy-functions-freetext-patterns]] — earlier session; antibiotic function overhaul
- [[uvira-sandbox]] — project index
