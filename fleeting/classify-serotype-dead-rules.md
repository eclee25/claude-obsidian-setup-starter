---
title: "classify_serotype: dead discordance rules"
type: fleeting
created: "2026-05-28"
---

# classify_serotype: dead discordance rules

`classify_serotype` (not in uvira-sandbox — lives in a separate repo) has two unreachable rules in the `cat_serotype` cross-lab merge:

- **Rule 3**: `cat_inaba_uvira == "Negative" & cat_inaba_inrb == "Inaba"` → "Inconclusive" — dead because rule 2 (`cat_inaba_uvira == "Inaba" | cat_inaba_inrb == "Inaba"`) fires first
- **Rule 7**: same issue for Ogawa

Additionally, the reverse discordance case (Uvira=Positive, INRB=Negative) is not written at all — also currently resolved as Positive via the OR rule.

**Proposed fix** (discussed 2026-05-28): move explicit discordance checks (both directions) before the OR rules. One lab positive + other lab Negative → Inconclusive. One lab positive + other lab Missing/Inconclusive → stays Positive.

To action when working in the relevant repository.
