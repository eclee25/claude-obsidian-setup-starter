"""
Improved R and Stan AST extractors for the graphifyy package.

These are NOT part of the distributed graphifyy. They live here so they can be
re-applied after every `pipx upgrade graphifyy`. See apply.py for the injector.

Design notes
------------
- Regex-based (no tree-sitter grammar exists for R or Stan).
- String literals and comments are stripped before scanning so `library(foo)`
  inside a string doesn't get mis-detected as an import.
- Function body ranges are found via brace/paren balance, not "up to the next
  top-level def" — that was the biggest source of mis-attributed calls.
- Stan name lookup uses a dict keyed on the bare function name, avoiding the
  old `nid.split("_")[-1]` bug that silently dropped every multi-underscore
  function (e.g. `log_lik_gp` was being looked up as `gp`).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


# ── shared helpers ────────────────────────────────────────────────────────────


def _make_id(*parts: str) -> str:
    """Mirror graphify's node-id convention: lowercase, [a-z0-9_] only."""
    joined = "_".join(str(p) for p in parts if p is not None)
    return re.sub(r"[^a-z0-9_]+", "_", joined.lower()).strip("_")


def _strip_strings_and_comments(
    source: str,
    line_comment: str,
    block_comment: tuple[str, str] | None = None,
    strip_strings: bool = True,
) -> list[str]:
    """
    Return source as a list of lines with:
      - string literals replaced by spaces (preserving column offsets)
        unless `strip_strings=False`,
      - line comments stripped to end of line,
      - block comments (if given) replaced by spaces (preserving newlines).

    Preserving column offsets matters because the downstream code reports
    source_location as `L{lineno}` and uses regex anchors like `^`. Keeping
    lines the same length also keeps line numbers stable.

    Callers that need to read string contents (e.g. `library("pkg")`,
    `setMethod("name", ...)`, `#include "file"`) should pass
    `strip_strings=False` and scan that view.
    """
    out_chars: list[str] = []
    i = 0
    n = len(source)
    in_string: str | None = None  # current quote char
    in_block_comment = False
    block_open, block_close = (block_comment or ("", ""))

    while i < n:
        c = source[i]
        nxt = source[i + 1] if i + 1 < n else ""

        # In a block comment: consume until close
        if in_block_comment:
            if block_close and source.startswith(block_close, i):
                out_chars.extend([" "] * len(block_close))
                i += len(block_close)
                in_block_comment = False
            else:
                # Preserve newlines so line numbers don't shift
                out_chars.append("\n" if c == "\n" else " ")
                i += 1
            continue

        # In a string literal: consume until matching quote
        if in_string is not None:
            if strip_strings:
                if c == "\\" and nxt:
                    out_chars.append("\n" if c == "\n" else " ")
                    out_chars.append("\n" if nxt == "\n" else " ")
                    i += 2
                    continue
                if c == in_string:
                    out_chars.append(" ")
                    in_string = None
                    i += 1
                    continue
                out_chars.append("\n" if c == "\n" else " ")
                i += 1
                continue
            else:
                # Preserve string contents verbatim
                if c == "\\" and nxt:
                    out_chars.append(c)
                    out_chars.append(nxt)
                    i += 2
                    continue
                if c == in_string:
                    out_chars.append(c)
                    in_string = None
                    i += 1
                    continue
                out_chars.append(c)
                i += 1
                continue

        # Not in string/comment. Look for openers.
        if block_comment and source.startswith(block_open, i):
            out_chars.extend([" "] * len(block_open))
            i += len(block_open)
            in_block_comment = True
            continue

        if line_comment and source.startswith(line_comment, i):
            # Consume to end of line (but preserve the newline)
            while i < n and source[i] != "\n":
                out_chars.append(" ")
                i += 1
            continue

        if c in ('"', "'"):
            in_string = c
            out_chars.append(" " if strip_strings else c)
            i += 1
            continue

        out_chars.append(c)
        i += 1

    return "".join(out_chars).splitlines()


def _match_brace_end(lines: list[str], start_line_idx: int, open_col: int) -> int:
    """
    Given the index of the line where a `{` appears at column `open_col`
    (0-indexed), return the 1-indexed line number where the matching `}` lives.
    Assumes `lines` already has strings/comments stripped so raw `{`/`}` counts
    are reliable.
    """
    depth = 0
    started = False
    for li in range(start_line_idx, len(lines)):
        line = lines[li]
        start_col = open_col if li == start_line_idx else 0
        for ch in line[start_col:]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth <= 0:
                    return li + 1
    return len(lines)  # unterminated — fall back to EOF


# ── R extractor ──────────────────────────────────────────────────────────────


# Functions that are not interesting as callees even if a user happened to
# define a local function by the same name. Kept conservative on purpose —
# we only suppress true builtins/common verbs.
_R_SKIP: frozenset[str] = frozenset({
    # testthat framework verbs — not interesting callees in a dependency graph
    "test_that", "describe", "it", "context", "setup", "teardown",
    "before_each", "after_each",
    "skip", "skip_if", "skip_if_not", "skip_on_ci", "skip_on_cran",
    "skip_if_no_token", "skip_on_covr",
    "expect_equal", "expect_identical", "expect_true", "expect_false",
    "expect_null", "expect_error", "expect_warning", "expect_message",
    "expect_match", "expect_length", "expect_named", "expect_is",
    "expect_s3_class", "expect_s4_class", "expect_contains", "expect_in",
    "expect_gt", "expect_lt", "expect_gte", "expect_lte", "expect_snapshot",
    "expect_no_error", "expect_no_warning", "expect_no_message",
    "expect_setequal", "expect_mapequal", "expect_vector", "expect_type",
    "expect_output", "expect_condition", "expect_silent", "expect_visible",
    "expect_invisible", "expect_equivalent",
    # control flow / constants
    "function", "if", "else", "for", "while", "repeat", "return", "break", "next",
    "TRUE", "FALSE", "NULL", "Inf", "NA", "NaN", "NA_integer_", "NA_real_",
    "NA_character_", "NA_complex_",
    # core constructors / IO
    "c", "list", "vector", "data.frame", "tibble", "matrix", "array",
    "print", "cat", "paste", "paste0", "sprintf", "format", "formatC",
    "stop", "warning", "message", "library", "require", "source", "suppressWarnings",
    "suppressMessages", "requireNamespace", "loadNamespace",
    # casts / predicates
    "as.numeric", "as.character", "as.integer", "as.logical", "as.Date",
    "as.POSIXct", "as.POSIXlt", "as.factor", "as.data.frame", "as.matrix",
    "is.null", "is.na", "is.numeric", "is.character", "is.logical",
    "is.function", "is.list", "is.vector", "is.data.frame", "is.matrix",
    "length", "nrow", "ncol", "names", "colnames", "rownames", "dim", "class",
    "head", "tail", "str", "summary",
    # base iteration / error handling
    "tryCatch", "try", "withCallingHandlers", "on.exit", "invisible",
    "readRDS", "saveRDS", "readLines", "writeLines", "readr", "here",
    # tidyverse staples (dplyr/tidyr/purrr/stringr/ggplot2)
    "filter", "select", "mutate", "arrange", "group_by", "ungroup",
    "summarise", "summarize", "left_join", "right_join", "inner_join",
    "full_join", "anti_join", "semi_join", "pivot_longer", "pivot_wider",
    "rename", "bind_rows", "bind_cols", "distinct", "slice",
    "map", "map2", "pmap", "map_dbl", "map_chr", "map_lgl", "map_int",
    "map_df", "walk", "walk2", "pwalk", "reduce", "accumulate",
    "lapply", "sapply", "vapply", "mapply", "do.call",
    "across", "case_when", "if_else", "rowwise", "across",
    "str_detect", "str_replace", "str_replace_all", "str_match",
    "str_extract", "str_sub", "str_trim", "str_split", "str_to_lower",
    "str_to_upper", "str_c", "str_glue",
    "ggplot", "aes", "geom_point", "geom_line", "geom_bar", "geom_col",
    "geom_histogram", "geom_density", "geom_ribbon", "geom_smooth",
    "geom_tile", "facet_wrap", "facet_grid", "scale_x_continuous",
    "scale_y_continuous", "theme", "labs", "coord_flip",
    "read_csv", "read_tsv", "read_delim", "write_csv", "write_tsv",
    # stats / math commonly used
    "mean", "median", "sd", "var", "quantile", "min", "max", "sum",
    "abs", "log", "exp", "sqrt", "round", "floor", "ceiling", "range",
    "pmin", "pmax", "seq", "seq_len", "seq_along", "rep", "rev", "sort",
    "order", "unique", "which", "any", "all", "table",
})


_R_CHUNK_RE = re.compile(r"^\s*```\s*\{\s*[rR][,\s}]")  # ```{r} or ```{R, opts}
_R_FUNC_DEF_RE = re.compile(
    # captures e.g. foo, obj$foo, pkg::foo, obj@foo
    r"^\s*([A-Za-z_.][A-Za-z0-9_.$@]*(?:::[A-Za-z_.][A-Za-z0-9_.]*)?)"
    r"\s*(?:<-|<<-|=)\s*function\s*\("
)
_R_SET_METHOD_CALL_RE = re.compile(r'^\s*setMethod\s*\(')
_R_SET_GENERIC_CALL_RE = re.compile(r'^\s*setGeneric\s*\(')
_R_QUOTED_NAME_RE = re.compile(r'\s*["\']([A-Za-z_.][A-Za-z0-9_.]*)["\']')
_R_CALL_RE = re.compile(r"(?<![A-Za-z0-9_.$@:])([A-Za-z_.][A-Za-z0-9_.]*)\s*\(")
# Call-site locators: match on the stripped view (strings blanked out so we
# never see `library(foo)` inside a string). Do NOT include `\s*` after `(`
# — on the stripped view, blanked-out string contents look like whitespace
# and a trailing `\s*` would gobble them, pushing m.end() past the argument.
_R_LIBRARY_CALL_RE = re.compile(
    r'(?<![A-Za-z0-9_.])(?:library|require|requireNamespace)\s*\('
)
_R_SOURCE_CALL_RE = re.compile(r'(?<![A-Za-z0-9_.])source\s*\(')
# After the `(` we read the arg: either a quoted string or a bare identifier.
_R_ARG_NAME_RE = re.compile(
    r'\s*["\']?([A-Za-z][A-Za-z0-9._/\\-]*)["\']?'
)


def _r_function_body_range(
    lines: list[str], def_line_idx: int, def_match_end: int
) -> int:
    """
    Given the zero-indexed line where a function def starts and the column
    just past `function(`, find the 1-indexed last line of the function body.

    Walks paren depth first (to reach `)`), then — if the next non-space char
    is `{` — brace depth until the matching close. For brace-less single-expr
    bodies (`f <- function(x) x + 1`), returns def_line_idx + 1.
    """
    # Step 1: walk to the `)` that closes the argument list.
    paren_depth = 1
    li = def_line_idx
    col = def_match_end
    while li < len(lines):
        line = lines[li]
        while col < len(line):
            ch = line[col]
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
                if paren_depth == 0:
                    col += 1
                    # Step 2: find the body opener.
                    # Skip whitespace, possibly across lines.
                    while li < len(lines):
                        rest = lines[li][col:]
                        stripped = rest.lstrip()
                        if not stripped:
                            li += 1
                            col = 0
                            continue
                        if stripped[0] == "{":
                            # Find column of `{` on this line
                            open_col = len(lines[li]) - len(stripped)
                            return _match_brace_end(lines, li, open_col)
                        # Single-expression body: ends at end of current line
                        # (R doesn't require brace for 1-expr bodies).
                        return li + 1
                    return len(lines)
            col += 1
        li += 1
        col = 0
    return len(lines)


def extract_r(path: Path) -> dict:
    """Regex-based extractor for .R / .r / .Rmd / .rmd files."""
    try:
        source = path.read_text(errors="replace")
    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e),
                "raw_calls": [], "input_tokens": 0, "output_tokens": 0}

    stem = path.stem
    str_path = str(path)
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_ids: set[str] = set()
    raw_calls: list[dict] = []

    def add_node(nid: str, label: str, line: int) -> None:
        if nid not in seen_ids:
            seen_ids.add(nid)
            nodes.append({
                "id": nid, "label": label, "file_type": "code",
                "source_file": str_path, "source_location": f"L{line}",
            })

    def add_edge(src: str, tgt: str, relation: str, line: int,
                 confidence: str = "EXTRACTED", weight: float = 1.0) -> None:
        edges.append({
            "source": src, "target": tgt, "relation": relation,
            "confidence": confidence, "confidence_score": 1.0,
            "source_file": str_path, "source_location": f"L{line}",
            "weight": weight,
        })

    file_nid = _make_id(str(path))
    add_node(file_nid, path.name, 1)

    # Two views: `stripped` has strings + comments stripped (for def/call
    # scanning), `with_strings` has only comments stripped (for library(),
    # source(), setMethod() — which need to read string contents).
    stripped = _strip_strings_and_comments(source, line_comment="#")
    with_strings = _strip_strings_and_comments(
        source, line_comment="#", strip_strings=False,
    )

    # For Rmd, mask out non-chunk lines on both views.
    if path.suffix.lower() in (".rmd", ".qmd"):
        def _mask(view: list[str]) -> list[str]:
            in_chunk = False
            out: list[str] = []
            for line in view:
                s = line.lstrip()
                if not in_chunk and _R_CHUNK_RE.match(line):
                    in_chunk = True
                    out.append("")
                    continue
                if in_chunk and s.startswith("```"):
                    in_chunk = False
                    out.append("")
                    continue
                out.append(line if in_chunk else "")
            return out
        stripped = _mask(stripped)
        with_strings = _mask(with_strings)

    # ── Function definitions ─────────────────────────────────────────────────
    # Each entry: (nid, bare_name, def_line_1idx, end_line_1idx)
    func_records: list[tuple[str, str, int, int]] = []

    def _register_func(full_name: str, line_1idx: int, end_1idx: int) -> str:
        # Normalise bare name for id/skip lookup: strip namespace, $, @ prefixes
        bare = re.sub(r"^.*[:$@]", "", full_name)
        nid = _make_id(stem, bare)
        add_node(nid, f"{full_name}()", line_1idx)
        add_edge(file_nid, nid, "contains", line_1idx)
        func_records.append((nid, bare, line_1idx, end_1idx))
        return nid

    for idx, line in enumerate(stripped):
        m = _R_FUNC_DEF_RE.match(line)
        if m:
            end = _r_function_body_range(stripped, idx, m.end())
            _register_func(m.group(1), idx + 1, end)
            continue
        # setMethod / setGeneric — locate call on stripped, read name from ws
        ws_line = with_strings[idx]
        cm = _R_SET_METHOD_CALL_RE.match(line)
        if cm:
            nm = _R_QUOTED_NAME_RE.match(ws_line, cm.end())
            if nm:
                end = _r_function_body_range(stripped, idx, cm.end())
                _register_func(nm.group(1), idx + 1, end)
                continue
        cm = _R_SET_GENERIC_CALL_RE.match(line)
        if cm:
            nm = _R_QUOTED_NAME_RE.match(ws_line, cm.end())
            if nm:
                _register_func(nm.group(1), idx + 1, idx + 1)

    # ── library() / require() ────────────────────────────────────────────────
    # Locate call sites on the stripped view, read the arg from with_strings.
    for idx, line in enumerate(stripped):
        ws_line = with_strings[idx]
        for m in _R_LIBRARY_CALL_RE.finditer(line):
            am = _R_ARG_NAME_RE.match(ws_line, m.end())
            if not am or not am.group(1):
                continue
            pkg = am.group(1)
            tgt = _make_id(pkg)
            add_node(tgt, pkg, idx + 1)
            add_edge(file_nid, tgt, "imports_from", idx + 1)

    # ── source("…") references ──────────────────────────────────────────────
    for idx, line in enumerate(stripped):
        ws_line = with_strings[idx]
        for m in _R_SOURCE_CALL_RE.finditer(line):
            # source() requires a string arg; match quoted literal only
            am = re.match(r'\s*["\']([^"\']+)["\']', ws_line[m.end():])
            if not am:
                continue
            ref = am.group(1)
            ref_path = Path(ref)
            tgt = _make_id(str(ref_path))
            add_node(tgt, ref_path.name, idx + 1)
            add_edge(file_nid, tgt, "references", idx + 1)

    # ── Intra-file function calls ────────────────────────────────────────────
    bare_to_nid = {bare: nid for nid, bare, _, _ in func_records}

    # Build a line → enclosing-function lookup. We use innermost enclosing
    # range so nested defs attribute calls to the nearest function.
    line_to_func: dict[int, str] = {}
    # Sort by (start asc, end asc) so later inner defs overwrite outer ones.
    for nid, _bare, start, end in sorted(func_records, key=lambda r: (r[2], r[3])):
        for ln in range(start + 1, end + 1):  # calls on def line itself are not body
            line_to_func[ln] = nid

    for idx, line in enumerate(stripped):
        caller_nid = line_to_func.get(idx + 1)
        for m in _R_CALL_RE.finditer(line):
            fname = m.group(1)
            if fname in _R_SKIP:
                continue
            callee_nid = bare_to_nid.get(fname)
            if callee_nid:
                # Intra-file edge
                src = caller_nid or file_nid
                if src != callee_nid:
                    add_edge(src, callee_nid, "calls", idx + 1)
            else:
                # Unresolved — graphify's cross-file resolver will look at this.
                # Use file_nid as fallback so calls inside test_that({}) closures
                # (which aren't function defs) still generate cross-file edges.
                raw_calls.append({
                    "caller_nid": caller_nid or file_nid, "callee": fname,
                    "source_file": str_path, "source_location": f"L{idx + 1}",
                })

    clean_edges = [e for e in edges
                   if e["source"] in seen_ids or e["confidence"] != "EXTRACTED"]
    return {"nodes": nodes, "edges": clean_edges, "raw_calls": raw_calls,
            "input_tokens": 0, "output_tokens": 0}


# ── Stan extractor ───────────────────────────────────────────────────────────


_STAN_BLOCKS = [
    "functions", "data", "transformed data", "parameters",
    "transformed parameters", "model", "generated quantities",
]
_STAN_BLOCK_RE = re.compile(
    r"^\s*(" + "|".join(re.escape(b) for b in _STAN_BLOCKS) + r")\s*\{"
)
# A function definition line is: return-type identifier(args...
# Return type can be: void | real | int | complex | vector | row_vector |
# matrix | tuple(...) | array[...] <basetype> | <basetype>[] (legacy).
_STAN_FUNC_RE = re.compile(
    r"^\s*(?:"
    r"void|real|int|complex|vector|row_vector|matrix|ordered|positive_ordered|"
    r"simplex|unit_vector|cholesky_factor_corr|cholesky_factor_cov|corr_matrix|"
    r"cov_matrix|tuple\s*\([^)]*\)|"
    r"array\s*\[[^\]]*\]\s+(?:void|real|int|complex|vector|row_vector|matrix)|"
    r"(?:real|int|complex|vector|row_vector|matrix)\s*\[\s*\]"
    r")\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_STAN_INCLUDE_RE = re.compile(r'^\s*#include\s+(?:[<"]([^>"]+)[>"]|([A-Za-z0-9_./-]+))')
_STAN_CALL_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# Sampling: `lhs ~ funcname(args)` — the name after `~` is the distribution,
# which is either a builtin or a user-defined `_lpdf` / `_lpmf`.
_STAN_SAMPLE_RE = re.compile(r"~\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(")

_STAN_SKIP: frozenset[str] = frozenset({
    "if", "else", "for", "while", "return", "break", "continue",
    "int", "real", "complex", "vector", "row_vector", "matrix", "array",
    "tuple", "ordered", "simplex", "void",
    "print", "reject", "target", "fatal_error",
    # common distributions
    "normal", "std_normal", "bernoulli", "bernoulli_logit", "poisson",
    "poisson_log", "neg_binomial", "neg_binomial_2", "neg_binomial_2_log",
    "binomial", "binomial_logit", "beta", "beta_binomial", "gamma",
    "inv_gamma", "exponential", "uniform", "lognormal", "student_t",
    "cauchy", "laplace", "chi_square", "inv_chi_square", "weibull",
    "pareto", "rayleigh", "dirichlet", "multinomial", "categorical",
    "categorical_logit", "ordered_logistic", "ordered_probit",
    "multi_normal", "multi_normal_cholesky", "multi_student_t",
    "lkj_corr", "lkj_corr_cholesky", "wishart", "inv_wishart",
    "von_mises", "gumbel", "frechet", "double_exponential",
    "skew_normal", "hypergeometric",
    # common math / linalg
    "log", "exp", "log1p", "log1m", "log_sum_exp", "log_mix", "log_diff_exp",
    "sqrt", "cbrt", "square", "abs", "fabs", "sign", "fmin", "fmax",
    "sum", "prod", "mean", "variance", "sd", "min", "max",
    "rep_vector", "rep_row_vector", "rep_matrix", "rep_array",
    "to_vector", "to_row_vector", "to_matrix", "to_array_1d", "to_array_2d",
    "segment", "head", "tail", "append_row", "append_col", "append_array",
    "size", "num_elements", "rows", "cols", "dims",
    "softmax", "log_softmax", "inv_logit", "logit", "Phi", "Phi_approx",
    "inv_Phi", "erf", "erfc", "tgamma", "lgamma", "digamma", "trigamma",
    "dot_product", "dot_self", "columns_dot_product", "rows_dot_product",
    "quad_form", "quad_form_diag", "quad_form_sym", "trace_quad_form",
    "diag_matrix", "diag_pre_multiply", "diag_post_multiply",
    "cholesky_decompose", "mdivide_left_tri_low", "mdivide_right_tri_low",
    "mdivide_left_spd", "mdivide_right_spd", "crossprod", "tcrossprod",
    "eigenvalues_sym", "eigenvectors_sym", "singular_values",
    "determinant", "log_determinant", "inverse", "inverse_spd",
    "transpose", "trace",
    # ODE integrators
    "integrate_ode", "integrate_ode_rk45", "integrate_ode_bdf",
    "integrate_ode_adams", "ode_rk45", "ode_rk45_tol", "ode_bdf",
    "ode_bdf_tol", "ode_adams", "ode_adams_tol", "ode_ckrk",
    "ode_ckrk_tol", "solve_ode", "algebra_solver", "algebra_solver_newton",
    # control / helpers
    "generated", "transformed", "parameters", "data", "model", "functions",
    "quantities",
})


def extract_stan(path: Path) -> dict:
    """Regex-based extractor for .stan files."""
    try:
        source = path.read_text(errors="replace")
    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e),
                "raw_calls": [], "input_tokens": 0, "output_tokens": 0}

    stem = path.stem
    str_path = str(path)
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_ids: set[str] = set()
    raw_calls: list[dict] = []

    def add_node(nid: str, label: str, line: int) -> None:
        if nid not in seen_ids:
            seen_ids.add(nid)
            nodes.append({
                "id": nid, "label": label, "file_type": "code",
                "source_file": str_path, "source_location": f"L{line}",
            })

    def add_edge(src: str, tgt: str, relation: str, line: int,
                 confidence: str = "EXTRACTED", weight: float = 1.0) -> None:
        edges.append({
            "source": src, "target": tgt, "relation": relation,
            "confidence": confidence, "confidence_score": 1.0,
            "source_file": str_path, "source_location": f"L{line}",
            "weight": weight,
        })

    file_nid = _make_id(str(path))
    add_node(file_nid, path.name, 1)

    lines = _strip_strings_and_comments(
        source, line_comment="//", block_comment=("/*", "*/"),
    )
    with_strings = _strip_strings_and_comments(
        source, line_comment="//", block_comment=("/*", "*/"),
        strip_strings=False,
    )

    # ── #include — scan the string-preserving view ──────────────────────────
    # Stan accepts three forms: #include "file", #include <file>, #include file
    # Resolve relative to the including file so the target node ID is
    # consistent with the file_nid generated when the included file is
    # extracted on its own.
    for idx, line in enumerate(with_strings):
        m = _STAN_INCLUDE_RE.match(line)
        if m:
            ref = m.group(1) or m.group(2)
            ref_path = Path(ref)
            resolved = path.parent / ref_path
            tgt = _make_id(str(resolved))
            add_node(tgt, ref_path.name, idx + 1)
            add_edge(file_nid, tgt, "references", idx + 1)

    # ── Top-level blocks ─────────────────────────────────────────────────────
    # Track block ranges by brace-matching on the stripped view.
    block_ranges: list[tuple[str, str, int, int]] = []  # (name, nid, start, end)
    block_nids: dict[str, str] = {}
    for idx, line in enumerate(lines):
        m = _STAN_BLOCK_RE.match(line)
        if m:
            bname = m.group(1)
            open_col = line.index("{")
            end = _match_brace_end(lines, idx, open_col)
            nid = _make_id(stem, bname.replace(" ", "_"))
            add_node(nid, f"{bname} block", idx + 1)
            add_edge(file_nid, nid, "contains", idx + 1)
            block_ranges.append((bname, nid, idx + 1, end))
            block_nids[bname] = nid

    # ── Function definitions inside the functions{} block ───────────────────
    func_block = next(((s, e) for n, _, s, e in block_ranges if n == "functions"),
                      None)
    func_block_nid = block_nids.get("functions", file_nid)
    # bare_name → nid
    bare_to_nid: dict[str, str] = {}
    # Each entry: (nid, bare, start, end)
    func_records: list[tuple[str, str, int, int]] = []

    if func_block is not None:
        fb_start, fb_end = func_block
        # Multi-line signatures: join consecutive non-blank lines inside the
        # block and try the regex against the joined form, then locate `{`
        # for the body.
        idx = fb_start  # 1-indexed start of block header
        while idx < fb_end:
            line = lines[idx]  # 0-indexed line content for index `idx` (header is at fb_start-1)
            # We want to iterate 0-indexed; translate:
            li0 = idx  # `idx` here is used as 0-indexed via the loop below
            # Normalise: re-enter a proper 0-indexed loop
            break
        for li0 in range(fb_start, fb_end):  # skip the header line itself
            line = lines[li0]
            # Build a candidate "joined signature" starting here. Stop when we
            # hit a `{` (start of body) or a semicolon (declaration only).
            if not line.strip():
                continue
            joined = line
            jlen = 1
            while "{" not in joined and ";" not in joined and li0 + jlen < fb_end:
                joined += " " + lines[li0 + jlen].strip()
                jlen += 1
                if jlen > 20:  # safety
                    break
            m = _STAN_FUNC_RE.match(joined)
            if not m:
                continue
            fname = m.group(1)
            # Find body line: first `{` at or after li0
            body_line_idx = li0
            while body_line_idx < fb_end and "{" not in lines[body_line_idx]:
                body_line_idx += 1
            if body_line_idx >= fb_end:
                continue
            open_col = lines[body_line_idx].index("{")
            end = _match_brace_end(lines, body_line_idx, open_col)
            nid = _make_id(stem, fname)
            add_node(nid, f"{fname}()", li0 + 1)
            add_edge(func_block_nid, nid, "contains", li0 + 1)
            bare_to_nid[fname] = nid
            func_records.append((nid, fname, li0 + 1, end))

    # ── Cross-block function calls ──────────────────────────────────────────
    # Calls inside model, transformed parameters, generated quantities that
    # reference user-defined functions.
    call_target_blocks = {"model", "transformed parameters", "generated quantities",
                          "transformed data"}

    def _enclosing_func_nid(line_1idx: int) -> str | None:
        # Prefer the innermost enclosing user function body if we're inside one
        best: str | None = None
        best_span = 10**9
        for nid, _bare, s, e in func_records:
            if s <= line_1idx <= e:
                span = e - s
                if span < best_span:
                    best_span = span
                    best = nid
        return best

    def _enclosing_block_nid(line_1idx: int) -> str | None:
        for bname, bnid, s, e in block_ranges:
            if bname in call_target_blocks and s <= line_1idx <= e:
                return bnid
        return None

    # User functions can also call each other inside functions{}, so scan that
    # block too for edges.
    scan_ranges: list[tuple[str, int, int]] = []  # (source_nid, start, end)
    for bname, bnid, s, e in block_ranges:
        if bname in call_target_blocks:
            scan_ranges.append((bnid, s, e))
    for nid, _bare, s, e in func_records:
        scan_ranges.append((nid, s, e))

    seen_edges: set[tuple[str, str, int]] = set()

    def _emit_call(src_nid: str, fname: str, line_1idx: int) -> None:
        if fname in _STAN_SKIP:
            return
        callee = bare_to_nid.get(fname)
        if callee and callee != src_nid:
            key = (src_nid, callee, line_1idx)
            if key in seen_edges:
                return
            seen_edges.add(key)
            add_edge(src_nid, callee, "calls", line_1idx)
        elif src_nid:
            raw_calls.append({
                "caller_nid": src_nid, "callee": fname,
                "source_file": str_path, "source_location": f"L{line_1idx}",
            })

    for src_nid, start, end in scan_ranges:
        for li0 in range(start - 1, min(end, len(lines))):
            line = lines[li0]
            # Prefer innermost user function as source if we're inside one
            inner = _enclosing_func_nid(li0 + 1)
            actual_src = inner or src_nid
            for m in _STAN_CALL_RE.finditer(line):
                _emit_call(actual_src, m.group(1), li0 + 1)
            for m in _STAN_SAMPLE_RE.finditer(line):
                # Sampling statements: the distribution name is a call target.
                # If a user defined `foo_lpdf`, the sampling `~ foo(...)` binds
                # to it; match both bare and _lpdf/_lpmf variants.
                dname = m.group(1)
                if dname in bare_to_nid:
                    _emit_call(actual_src, dname, li0 + 1)
                else:
                    for suffix in ("_lpdf", "_lpmf"):
                        if dname + suffix in bare_to_nid:
                            _emit_call(actual_src, dname + suffix, li0 + 1)
                            break

    return {"nodes": nodes, "edges": edges, "raw_calls": raw_calls,
            "input_tokens": 0, "output_tokens": 0}


# ── Self-test ────────────────────────────────────────────────────────────────


def _selftest() -> None:
    """Run against a couple of synthetic fixtures. Raises on regression."""
    import tempfile

    # R fixture: tests comment-in-string, function body range, setMethod,
    # $ methods, and tidyverse skip.
    r_src = '''
# a top-level comment
library(dplyr)
library("tibble")
msg <- "library(ignored)"   # string must not be scanned
helper <- function(x) {
  filter(x, y > 0)          # tidyverse verb, skipped
  inner(x) + other(x)       # both should produce raw_calls
}
inner <- function(x) x + 1  # single-expr body
obj$method <- function(y) helper(y)
setMethod("myGen", "ANY", function(x) inner(x))
z <- 1  # top-level, not in any function
trailing <- helper(z)  # call at top level -> file-level edge
source("utils/foo.R")
source("utils/bar.R")
'''
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False) as f:
        f.write(r_src)
        rpath = Path(f.name)
    try:
        result = extract_r(rpath)
    finally:
        rpath.unlink()

    labels = {n["label"] for n in result["nodes"]}
    assert "helper()" in labels, f"helper missing: {labels}"
    assert "inner()" in labels, f"inner missing: {labels}"
    assert "obj$method()" in labels, f"obj$method missing: {labels}"
    assert "myGen()" in labels, f"setMethod not captured: {labels}"
    # Two distinct source() targets must not collide
    src_targets = [n for n in result["nodes"] if n["label"] in ("foo.R", "bar.R")]
    assert len(src_targets) == 2, f"source() collision: {src_targets}"
    # "library(ignored)" inside string must NOT be imported
    pkg_labels = {n["label"] for n in result["nodes"]
                  if any(e.get("relation") == "imports_from"
                         and e.get("target") == n["id"] for e in result["edges"])}
    assert "ignored" not in pkg_labels, f"string-leak import: {pkg_labels}"
    assert {"dplyr", "tibble"} <= pkg_labels, f"missing pkg: {pkg_labels}"

    # Stan fixture: multi-underscore function, sampling statement, multi-line
    # signature, tuple string with brace doesn't break block detection.
    stan_src = '''
functions {
  real log_lik_gp(vector y,
                  vector mu,
                  real sigma) {
    return normal_lpdf(y | mu, sigma);
  }
  real my_dist_lpdf(real y, real mu) {
    return -0.5 * square(y - mu);
  }
}
data {
  int<lower=0> N;
  vector[N] y;
  // comment with a } brace that must not break the counter
  string s = "}}}}";  // not real stan, but our stripper should swallow it
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  target += log_lik_gp(y, rep_vector(mu, 10), sigma);
  y ~ my_dist(mu);   // user-defined distribution via _lpdf
}
'''
    with tempfile.NamedTemporaryFile("w", suffix=".stan", delete=False) as f:
        f.write(stan_src)
        spath = Path(f.name)
    try:
        result = extract_stan(spath)
    finally:
        spath.unlink()

    labels = {n["label"] for n in result["nodes"]}
    assert "log_lik_gp()" in labels, f"multi-underscore fn missing: {labels}"
    assert "my_dist_lpdf()" in labels, f"_lpdf fn missing: {labels}"
    # Must find call from model block to log_lik_gp
    call_edges = [(e["source"], e["target"]) for e in result["edges"]
                  if e["relation"] == "calls"]
    # find log_lik_gp nid
    log_lik_nid = next(n["id"] for n in result["nodes"]
                       if n["label"] == "log_lik_gp()")
    assert any(t == log_lik_nid for _, t in call_edges), \
        f"model -> log_lik_gp call not found: {call_edges}"
    # Must find sampling statement edge to my_dist_lpdf
    my_dist_nid = next(n["id"] for n in result["nodes"]
                       if n["label"] == "my_dist_lpdf()")
    assert any(t == my_dist_nid for _, t in call_edges), \
        f"~ sampling edge not found: {call_edges}"
    # All 6 blocks should be present (functions, data, parameters, model only
    # here — not all 7).
    block_labels = {l for l in labels if l.endswith("block")}
    assert {"functions block", "data block", "parameters block",
            "model block"} <= block_labels, f"missing blocks: {block_labels}"

    # Stan fixture: bare #include (no quotes) — the common CmdStan form.
    # Verify that a "references" edge is created with a target ID that matches
    # the file_nid that would be generated for the included file.
    stan_inc_src = '#include functions/model_utils.stan\nfunctions {}\n'
    with tempfile.NamedTemporaryFile("w", suffix=".stan", delete=False,
                                     dir=tempfile.gettempdir()) as f:
        f.write(stan_inc_src)
        inc_path = Path(f.name)
    try:
        result = extract_stan(inc_path)
    finally:
        inc_path.unlink()

    expected_resolved = inc_path.parent / Path("functions/model_utils.stan")
    expected_tgt = _make_id(str(expected_resolved))
    ref_edges = [e for e in result["edges"] if e["relation"] == "references"]
    assert any(e["target"] == expected_tgt for e in ref_edges), \
        f"bare #include edge not found (expected tgt={expected_tgt!r}): {ref_edges}"

    # R fixture: testthat — calls inside test_that({}) must generate raw_calls
    # attributed to file_nid, not be silently dropped (degree-0 test files).
    r_test_src = '''
library(testthat)
test_that("basic check", {
  result <- compute_result(42)
  expect_equal(result, 100)
  expect_true(validate_output(result))
})
test_that("edge case", {
  x <- preprocess_data(NULL)
  expect_null(x)
})
'''
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False) as f:
        f.write(r_test_src)
        tpath = Path(f.name)
    try:
        result = extract_r(tpath)
    finally:
        tpath.unlink()

    callees = {rc["callee"] for rc in result["raw_calls"]}
    assert "compute_result" in callees, \
        f"test_that body call 'compute_result' missing from raw_calls: {callees}"
    assert "validate_output" in callees, \
        f"test_that body call 'validate_output' missing from raw_calls: {callees}"
    assert "preprocess_data" in callees, \
        f"test_that body call 'preprocess_data' missing from raw_calls: {callees}"
    # testthat verbs must be skipped
    assert "test_that" not in callees, f"test_that leaked into raw_calls: {callees}"
    assert "expect_equal" not in callees, f"expect_equal leaked into raw_calls: {callees}"
    # All raw_calls from testthat closures should be attributed to file_nid
    file_nid = _make_id(str(tpath))
    for rc in result["raw_calls"]:
        if rc["callee"] in ("compute_result", "validate_output", "preprocess_data"):
            assert rc["caller_nid"] == file_nid, \
                f"raw_call for {rc['callee']!r} has unexpected caller {rc['caller_nid']!r}"

    # R fixture: .qmd — R chunks should be extracted, non-chunk lines ignored.
    qmd_src = '''---
title: "Analysis"
format: html
---

Some prose here.

```{r setup}
library(dplyr)
my_helper <- function(x) x + 1
```

More prose.

```{r results}
out <- my_helper(10)
```
'''
    with tempfile.NamedTemporaryFile("w", suffix=".qmd", delete=False) as f:
        f.write(qmd_src)
        qpath = Path(f.name)
    try:
        result = extract_r(qpath)
    finally:
        qpath.unlink()

    labels = {n["label"] for n in result["nodes"]}
    assert "my_helper()" in labels, f".qmd function not extracted: {labels}"
    pkg_labels = {n["label"] for n in result["nodes"]
                  if any(e.get("relation") == "imports_from"
                         and e.get("target") == n["id"] for e in result["edges"])}
    assert "dplyr" in pkg_labels, f".qmd library() not extracted: {pkg_labels}"

    print("extractors selftest: OK")


if __name__ == "__main__":
    _selftest()
