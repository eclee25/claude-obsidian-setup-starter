---
title: "2026-05-22 Pandoc YAML rendering fixes"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-22"
updated: "2026-05-22"
type: session-log
project: uvira-sandbox
---

# 2026-05-22 — Pandoc YAML rendering fixes

## What was done

### Bug fixes (`R/4_data_exploration.qmd`)

**`eval(bquote(...))` pattern applied to model fitting loops:**
- `fit-model1` chunk: renamed loop variable `var` → `covar` (was shadowing `stats::var()`); wrapped `coxph()` call in `eval(bquote(.(f)))` so the evaluated formula is embedded at call time rather than referencing the loop variable by name. Fixes `ggsurvfit` re-evaluation error.
- `fit-model3` chunk: same treatment; renamed `f` → `f_str` to avoid shadowing.

**`fig-model3-all` chunk option notation fix:**
- Changed `fig-width: 6` → `fig.width: 6` and `fig-height: 4` → `fig.height: 4` to match knitr dot-notation convention used throughout the rest of the document (Quarto kebab-case was inconsistent).

**Pandoc YAML interference fix (`R/4_data_exploration.qmd:1092`):**
- Root cause: `print(summary(coxph_fit))` always emits a `---` line (the "Signif. codes" separator). In a `results: asis` chunk this `---` appears as raw markdown in the knitr output. Pandoc then interprets it as a YAML metadata block delimiter, attempts to parse the following lines as YAML, and fails: `YAML parse exception at line 5, column 0, while scanning a simple key: could not find expected ':'`.
- Fix: wrapped both `print(summary(fit))` and `print(cox.zph(fit))` in fenced code blocks via `cat()` calls:
  ```r
  cat("\n\n```\n")
  print(summary(fit))
  cat("```\n\n```\n")
  print(cox.zph(fit))
  cat("```\n\n")
  ```
- Chunks without `results: asis` are safe — knitr captures their output in verbatim blocks automatically.

**Minor fixes:**
- Added missing `#| label: tab-admit-after-swab` chunk label.
- Restored subtitle: `"Exploratory analysis"` (was accidentally blanked).

### `R/survival_utils.R`

- Updated x-axis label in `plot_coxph()`: `"Days from symptom onset to CTC discharge"` → `"Days from admission to CTC discharge"` (consistent with time-axis restructure to `t_admit_discharge`).
- Removed `plot_coxph_strat()` function — obsolete after stratification was deferred; the function referenced the old `t_onset_discharge` axis and would have produced misleading plots.

### Vault

- Created [[quarto-results-asis-yaml-pitfall]] — technical note documenting the `results: asis` + `---` YAML interference pitfall, known R outputs that trigger it (`summary(coxph_fit)`), and the fix pattern.

## Decisions made

- `print(summary(fit))` and similar R outputs that produce bare `---` lines **must** be wrapped in fenced code blocks when used inside `results: asis` chunks.
- `plot_coxph_strat()` confirmed obsolete and removed.

## Pending / open questions

(Carried forward from [[2026-05-22-survival-analysis-restructure]])

- `temp_clean_discharge()` is commented out — manual patches for records C-12575, C-12557, C-24384 not being applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose; may want a separate level for zero.
- `ors_f2` structure not yet confirmed — factor levels unknown until data is inspected.
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs before finalising stratification decisions.

## Files changed

- `R/4_data_exploration.qmd` — eval(bquote) pattern, fig option notation, fenced code block wrapping, subtitle, label
- `R/survival_utils.R` — x-axis label, removed `plot_coxph_strat()`
