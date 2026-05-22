---
title: "Quarto: results: asis and YAML interference from R text output"
tags:
  - quarto
  - knitr
  - pandoc
  - rendering
created: "2026-05-22"
updated: "2026-05-22"
status: active
type: technical
project: uvira-sandbox
---

# Quarto: `results: asis` and YAML interference from R text output

## The pitfall

When a knitr chunk uses `results: asis`, all text output is emitted as **raw markdown** into the pandoc-processed intermediate document. If any R print function produces a line containing `---` (three hyphens on their own line), pandoc interprets it as the start of a [YAML metadata block](https://pandoc.org/MANUAL.html#yaml-metadata-blocks). The content that follows until the next `---` or `...` delimiter is then parsed as YAML — and if that content is not valid YAML, rendering fails with a cryptic error.

**Symptom:**
```
Error running Lua:
YAML parse exception at line 5, column 0,
while scanning a simple key:
could not find expected ':'
stack traceback:
    ...readqmd.lua:167: in function 'readqmd.readqmd'
    ...qmd-reader.lua:13: in function 'Reader'
```

The error occurs **after** knitr execution succeeds — it is a pandoc post-processing failure, not a chunk evaluation failure.

## Known R outputs that produce `---`

- **`print(summary(coxph_fit))`** — always includes a `---` separator line above the "Signif. codes" legend
- Any R model or test summary that uses `---` as a visual section divider in its print method

## Fix

Wrap the problematic `print()` call inside fenced code blocks via `cat()`:

```r
cat("\n\n```\n")
print(summary(fit))
cat("```\n\n```\n")
print(cox.zph(fit))
cat("```\n\n")
```

This makes the `---` line inert — it sits inside a verbatim block where pandoc does not interpret it as a delimiter.

## Why chunks WITHOUT `results: asis` are safe

Without `results: asis`, knitr captures text output and wraps it in a `<pre>` / fenced code block automatically. The `---` is never exposed as raw markdown. The problem is specific to `results: asis` because that option bypasses knitr's output capture entirely.

## File citation

`R/4_data_exploration.qmd:1071` — `fig-model3-all` chunk: first instance of this pattern encountered and fixed (2026-05-22).

## Related

- [[survival-analysis-restructure-2026-05]] — context in which this was discovered (Model 3 loop with `results: asis`)
- [[uvira-sandbox]] — project where this was first encountered
