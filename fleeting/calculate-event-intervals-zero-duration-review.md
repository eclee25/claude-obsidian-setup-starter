---
title: "calculate_event_intervals — review zero-duration CTC stays"
type: fleeting
created: "2026-05-28"
---

# calculate_event_intervals — review zero-duration CTC stays

There are very few patients with `t_admit_discharge = 0` (admitted and discharged on the same calendar day). Before finalising survival models, verify whether these are:

1. **True same-day discharges** — patient arrived and was discharged within one calendar day. Biologically plausible but rare at a CTC.
2. **Data entry errors** — admission and discharge dates recorded identically due to form error.
3. **An artefact of whole-day truncation** — `calculate_event_intervals()` uses `as.Date()` on POSIXct datetimes before differencing, so a patient admitted at 23:00 and discharged at 01:00 the next day would get `t_admit_discharge = 1`, but a patient admitted at 08:00 and discharged at 22:00 would get `t_admit_discharge = 0`. This is the intended behaviour (confirmed 2026-05-28), but the 0-day group may warrant inspection.

**Check to run:**
```r
df_survival %>%
  filter(t_admit_discharge == 0) %>%
  select(record_id, dt_admission_f1, dttm_outcome_f2, rdt_cleared, dehydration) %>%
  arrange(dt_admission_f1)
```

**Action:** If 0-day patients look like genuine rapid discharges, consider whether they should be excluded from the survival analysis or handled as a special case (e.g., tied event at time 0). If they look like data errors, flag for `temp_clean_discharge()`.

See also: `temp_clean_discharge()` currently commented out in `clean-clinical-data` pipeline — patches C-12575, C-12557, C-24384 intentionally skipped?

File: `R/2_clinical_utils.R` (`calculate_event_intervals`), `R/4_data_exploration.qmd` (`prep-surv-data`)
