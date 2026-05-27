---
title: "2026-05-27 Azith/doxy functions, free-text pattern overhaul, diagnostic chunk"
tags:
  - session-log
  - uvira-sandbox
created: "2026-05-27"
updated: "2026-05-27"
type: session-log
project: uvira-sandbox
---

# 2026-05-27 — Azith/doxy functions, free-text pattern overhaul, diagnostic chunk

## What was done

### New functions: `clean_antibiotics_azith_f2` and `clean_antibiotics_doxy_f2` (`R/2_clinical_utils.R`)

Added two drug-specific f2 functions (CTC admission only — no f1 counterparts requested):

- `clean_antibiotics_azith_f2`: checkbox `antibiotics_name_f2___azithromycin` OR `"azithromycin"` in `antibiotic_name_other_f2` → `cat_antibiotics_azith_f2` (Yes/No)
- `clean_antibiotics_doxy_f2`: checkbox `antibiotics_name_f2___doxycyclin` OR `"doxycyclin"` in `antibiotic_name_other_f2` → `cat_antibiotics_doxy_f2` (Yes/No)

Both added to the pipeline in `R/4_data_exploration.qmd` after `clean_antibiotics_ineffUvira_f2()`.

### Diagnostic chunk: free-text unmatched strings (`R/4_data_exploration.qmd`)

Added `## Diagnostic: free-text antibiotic fields — unmatched strings` section before the antibiotic overview. Chunk label `diag-abx-freetext-unmatched` runs against `df_clinic` (not `df_clean`, which drops the raw antibiotic columns). Outputs unmatched strings from `medicines_other_f1` and `antibiotic_name_other_f2` alphabetically.

### Bug fix: missing `|` separator in f2 paste0() calls (`R/2_clinical_utils.R`)

In `clean_antibiotics_any_f2`, `clean_antibiotics_gtfcc_f2`, and `clean_antibiotics_uvira_f2`, the `paste0()` for known/non-GTFCC/uvira patterns was missing a `|` before `"cotri|erytro|..."`, producing `"tinizolcotri"` / `"shalcipcotri"` which never matched real data. Added trailing `|` to fix. `cotri` (cotrimoxazole) and `shalcip` are now correctly captured in all f2 functions.

### Free-text pattern overhaul — all 8 antibiotic cleaning functions (`R/2_clinical_utils.R`)

Applied symmetrically to f1 and f2 functions throughout. Exception: `"antibiotiques non connus"` added as `Unknown` to f1 `uncertain_pattern` only (f2 functions have no Unknown level).

**New drug variants / misspellings added:**

| Pattern added | Classification | Notes |
|--------------|----------------|-------|
| `erytho\|erytro\|erythro\|eruthro\|heritro` | Effective (Uvira), non-GTFCC | Erythromycin variants — previously absent from f1; already in f2 |
| `chalcip\|chalsip\|shacip` | Same as `shalcip` (cipro) | Brand name variants |
| `cipro` | GTFCC / effective | Shorthand for ciprofloxacin |
| `cloxacil` (replaces `cloxacilline`) | Ineffective | Captures both `cloxacilline` and `cloxaciline` |
| `cotri\|trimoxazole` | Effective (cotrimoxazole) | `cotri` added to f1; `trimoxazole` added to both |
| `ampicilline` | Effective in Uvira (non-GTFCC) | Active until spring 2025; still coded as effective |
| `penicillin` | Ineffective | Any antibiotic, not effective against cholera |
| `gentamicine` | Same as `gentamycine` (effective) | Spelling variant |
| `metazol\|metronidazol\|métronidazole` | Ineffective | Metronidazole variants |
| `négram\|negeam` | Same as `negram` (nalidixic acid, effective) | Accented and typo variants |
| `tinidazol\|tanzol\|trinidazol\|tunidazol` | Ineffective (nitroimidazole) | Tinidazole variants and brand name |
| `antibiotiques non connus` | Unknown (f1 only) | Uncertain antibiotic — can't classify |

**Identified as non-antibiotic (not added):**
- `albendazol` — anthelmintic; correctly stays unmatched / "No"

## Decisions made

- f1/f2 pattern symmetry: drug classification is a property of the molecule, not timing. Same patterns applied to both forms, except "antibiotiques non connus" → Unknown which requires f2 structural changes (no Unknown level currently).
- `tetracyclin` checkbox NOT included in `clean_antibiotics_doxy_f2` — tetracycline and doxycycline are separate drugs despite being in the same class.

## Pending / open questions

(Carried forward)

- `temp_clean_discharge()` commented out — patches for C-12575, C-12557, C-24384 not applied. Intentional?
- `ringer_bin` lowest bin `(-Inf, 1000]` conflates zero Ringer's with low-dose.
- `ors_f2` factor levels not yet confirmed.
- Run Model 1 and Model 3 fits; check `cox.zph()` outputs.
- f2 Unknown level: decide whether to add Unknown to `any_f2`, `gtfcc_f2`, `uvira_f2` for unidentifiable free-text entries.

## Files changed

- `R/2_clinical_utils.R` — new azith/doxy functions, cotri separator fix, comprehensive pattern updates across all 8 antibiotic cleaning functions
- `R/4_data_exploration.qmd` — new azith/doxy pipeline calls, diagnostic chunk, diagnostic union patterns updated throughout
