---
title: "2026-05-28 Model 1 spec cleanup after render review"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-28"
updated: "2026-05-28"
type: session-log
project: uvira-sandbox
---

# 2026-05-28 — Model 1 spec cleanup after render review

## What was done

### `model1-spec` trimmed (`R/4_data_exploration.qmd`)

User reviewed rendered output and made the following manual edits:

- `vaccinated_25_f1` (p3) commented out — confirmed too sparse in the analysis cohort
- `outbreak_wk20` (q1) and `outbreak_wk40` (q3) commented out — keeping only `outbreak_wk30` (q2) as the representative threshold
- Removed two stale preliminary bullet points ("Consider stratifying...", "Consider adjusting for...") above the `model1-spec` chunk

## Pending / open questions

(Carried forward)

- **Review survival model additions from 2026-05-28 session** — model3-spec additions (3j1, 3j2, 3k, 3l) not yet reviewed
- Implement `classify_serotype` discordance fix in external repository (see [[classify-serotype-dead-rules]])
- Run `diag-abx-freetext-unmatched` → revisit [[clean-antibiotics-ineffuvira-drift-risk]]
- Review zero-duration CTC stays (see [[calculate-event-intervals-zero-duration-review]])
- `ringer_bin` lowest bin conflates zero Ringer's with low-dose
- `temp_clean_discharge()` commented out — intentional?
- Verify `ind_register_2023_f1` values to check `classify_vaccination` coverage

## Files changed

- `R/4_data_exploration.qmd` — model1-spec trim (user edits)

## Related

- [[uvira-sandbox]] — project index
