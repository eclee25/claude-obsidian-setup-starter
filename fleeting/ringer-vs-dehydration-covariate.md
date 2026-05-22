---
title: "Consider ringer_bin instead of dehydration as severity proxy"
tags:
  - uvira-sandbox
created: "2026-05-22"
type: fleeting
---

Consider using `ringer_bin` instead of `dehydration` as the primary severity indicator in the survival models, even though this is less ideal from a disease timeline standpoint (Ringer's is administered *during* the CTC stay, after admission, so it is not strictly a pre-admission severity measure). Dehydration is assessed at admission and is more biologically proximal to severity, but Ringer's volume may be a more objective/quantitative marker. The two are likely collinear. Worth testing in a sensitivity model.
