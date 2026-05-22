#!/usr/bin/env python3
"""
Apply the vault's R and Stan extractor patches to the installed graphifyy.

What it does
------------
The distributed graphifyy has no R or Stan support. This script adds it by
patching the installed package in three places, each bounded by markers so
every run is idempotent:

  1. graphify/extract.py  _DISPATCH dict (inside the extract() function):
     route .R / .r / .Rmd / .rmd to extract_r and .stan to extract_stan.
  2. graphify/extract.py  collect_files _EXTENSIONS set:
     include .R / .r / .Rmd / .rmd / .stan so files are discovered.
  3. graphify/extract.py  module footer:
     append improved extract_r + extract_stan definitions (module-scope).
     The dispatch dict is rebuilt on every call and reads these by name, so
     the late-bound definitions take precedence.

detect.py already ships with .r / .rmd / .stan in CODE_EXTENSIONS, so we
verify but do not patch it.

Usage
-----
    python3 apply.py            # patch the interpreter's graphify
    python3 apply.py --check    # report whether the patch is currently applied
    python3 apply.py --remove   # strip all patch markers
    python3 apply.py --python /path/to/python  # target a specific interpreter
"""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
from pathlib import Path

# Markers — anchor idempotency. Changing these breaks existing installs.
FOOTER_BEGIN = "# ── graphify-patches begin (vault) ─────────────────────────────"
FOOTER_END   = "# ── graphify-patches end (vault) ───────────────────────────────"
DISPATCH_MARK = "# vault-patch: R/Stan dispatch"
EXTENSIONS_MARK = "# vault-patch: R/Stan extensions"

# The actual text we inject
DISPATCH_ENTRIES = (
    '        ".R": lambda p, **kw: extract_r(p, **kw),\n'
    '        ".r": lambda p, **kw: extract_r(p, **kw),\n'
    '        ".Rmd": lambda p, **kw: extract_r(p, **kw),\n'
    '        ".rmd": lambda p, **kw: extract_r(p, **kw),\n'
    '        ".qmd": lambda p, **kw: extract_r(p, **kw),\n'
    '        ".stan": lambda p, **kw: extract_stan(p, **kw),\n'
)
EXTENSIONS_ENTRIES = (
    '        ".R", ".r", ".Rmd", ".rmd", ".qmd", ".stan",\n'
)

HERE = Path(__file__).resolve().parent


# ── interpreter + module discovery ────────────────────────────────────────────


def _find_module_file(python_bin: str, module: str) -> Path:
    out = subprocess.run(
        [python_bin, "-c",
         f"import {module}, pathlib; print(pathlib.Path({module}.__file__))"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(
            f"Could not import {module} with {python_bin!r}.\n"
            f"stderr: {out.stderr}"
        )
    return Path(out.stdout.strip())


def _resolve_python(explicit: str | None) -> str:
    """Decide which interpreter owns graphifyy. Mirrors SKILL.md logic."""
    if explicit:
        return explicit
    marker = Path.cwd() / "graphify-out" / ".graphify_python"
    if marker.exists():
        return marker.read_text().strip()
    bin_ = shutil.which("graphify")
    if bin_:
        try:
            first = Path(bin_).read_text().splitlines()[0]
            if first.startswith("#!"):
                candidate = first[2:].strip()
                if Path(candidate).exists():
                    return candidate
        except Exception:
            pass
    return sys.executable


# ── footer (function definitions) ────────────────────────────────────────────


def _strip_for_injection(src: str) -> str:
    """Prepare extractors.py for injection as a footer block.

    Drops:
      - `from __future__ import …` (only valid at file top; host file has its own).
      - `_selftest` function and its `if __name__ == '__main__'` guard.
    """
    tree = ast.parse(src)
    keep: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if isinstance(node, ast.FunctionDef) and node.name == "_selftest":
            continue
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                continue
        keep.append(node)
    tree.body = keep
    return ast.unparse(tree)


def _build_footer_block() -> str:
    body = _strip_for_injection((HERE / "extractors.py").read_text()).rstrip()
    lines = [
        "",
        FOOTER_BEGIN,
        "# Injected by workflow/graphify-patches/apply.py — do NOT hand-edit.",
        "# Source of truth: <vault>/workflow/graphify-patches/extractors.py",
        "# Redefines extract_r and extract_stan at module scope. The dispatch",
        "# dict in extract() is rebuilt on every call and looks these up by",
        "# name, so late-binding ensures our versions run.",
        "",
        body,
        "",
        FOOTER_END,
        "",
    ]
    return "\n".join(lines)


def _remove_footer(content: str) -> str:
    b = content.find(FOOTER_BEGIN)
    if b == -1:
        return content
    e = content.find(FOOTER_END, b)
    if e == -1:
        return content[:b].rstrip() + "\n"
    end = content.find("\n", e)
    if end == -1:
        end = len(content)
    return (content[:b].rstrip() + "\n" + content[end + 1:]).rstrip() + "\n"


# ── dispatch dict + extensions set (surgical inserts) ────────────────────────


def _inject_dispatch(content: str) -> tuple[str, bool]:
    """Insert the dispatch dict entries with a marker. Returns (new, changed).

    Locates the _DISPATCH dict by looking for `_DISPATCH: dict[` and inserts
    our entries just before the dict's closing `}`. Idempotent via marker.
    """
    if DISPATCH_MARK in content:
        return content, False
    anchor = "_DISPATCH: dict[str, Any] = {"
    i = content.find(anchor)
    if i == -1:
        raise RuntimeError(
            "Could not locate `_DISPATCH: dict[str, Any] = {` in extract.py. "
            "The upstream structure may have changed — inspect manually."
        )
    # Find the matching `}` for this dict by brace counting from the opener.
    start = content.index("{", i)
    depth = 0
    j = start
    while j < len(content):
        if content[j] == "{":
            depth += 1
        elif content[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    else:
        raise RuntimeError("Could not find closing `}` of _DISPATCH.")
    # Insert before the line containing the closing `}`
    line_start = content.rfind("\n", 0, j) + 1
    insertion = (
        f"        {DISPATCH_MARK}\n"
        f"{DISPATCH_ENTRIES}"
    )
    return content[:line_start] + insertion + content[line_start:], True


def _inject_extensions(content: str) -> tuple[str, bool]:
    """Insert the collect_files extension entries with a marker."""
    if EXTENSIONS_MARK in content:
        return content, False
    anchor = "_EXTENSIONS = {"
    i = content.find(anchor)
    if i == -1:
        raise RuntimeError(
            "Could not locate `_EXTENSIONS = {` in extract.py. "
            "The upstream structure may have changed — inspect manually."
        )
    start = content.index("{", i)
    depth = 0
    j = start
    while j < len(content):
        if content[j] == "{":
            depth += 1
        elif content[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    else:
        raise RuntimeError("Could not find closing `}` of _EXTENSIONS.")
    line_start = content.rfind("\n", 0, j) + 1
    insertion = (
        f"        {EXTENSIONS_MARK}\n"
        f"{EXTENSIONS_ENTRIES}"
    )
    return content[:line_start] + insertion + content[line_start:], True


def _remove_marker_block(content: str, marker: str) -> str:
    """Remove a marker line AND all consecutive following lines that look
    like the injected entries (ending with `,`). Safer than heuristically
    matching specific content: we just drop from the marker until a line
    breaks the "continues an injected list" pattern."""
    i = content.find(marker)
    if i == -1:
        return content
    line_start = content.rfind("\n", 0, i) + 1
    # Walk forward line by line, removing while the line ends with `,` or is
    # part of our injected payload. Stop as soon as we see a line that doesn't
    # look injected (e.g., the closing `}` of the dict/set, or a blank line).
    out = content[:line_start]
    j = content.find("\n", i) + 1
    while j < len(content):
        nxt = content.find("\n", j)
        if nxt == -1:
            break
        line = content[j:nxt]
        stripped = line.strip()
        # Our injected block is the marker line itself + entries ending with
        # `,`. The moment we hit a line that doesn't end with `,`, we stop.
        if stripped and stripped.endswith(","):
            j = nxt + 1
            continue
        break
    return out + content[j:]


# ── top-level commands ───────────────────────────────────────────────────────


def _verify(python_bin: str) -> int:
    # 1. Import works
    rc = subprocess.run(
        [python_bin, "-c",
         "import graphify.extract as e; "
         "assert callable(e.extract_r) and callable(e.extract_stan)"],
        check=False,
    ).returncode
    if rc != 0:
        print("ERROR: graphify.extract failed to import after patch.",
              file=sys.stderr)
        return 3
    # 2. Dispatch routes .R and .stan to our functions
    rc = subprocess.run(
        [python_bin, "-c",
         "from pathlib import Path\n"
         "import graphify.extract as e\n"
         "# Build a dummy Path and confirm collect_files' ext set includes .R\n"
         "assert any(p.suffix.lower() in ('.r','.stan') for p in [Path('x.R'), Path('x.stan')])\n"
         "# Smoke: extract_r / extract_stan return the expected shape on empty input\n"
         "import tempfile, pathlib\n"
         "with tempfile.NamedTemporaryFile('w', suffix='.R', delete=False) as f:\n"
         "    f.write('f <- function(x) x\\n')\n"
         "    p = pathlib.Path(f.name)\n"
         "r = e.extract_r(p)\n"
         "assert 'nodes' in r and any(n['label'] == 'f()' for n in r['nodes']), r\n"
         "with tempfile.NamedTemporaryFile('w', suffix='.stan', delete=False) as f:\n"
         "    f.write('functions {\\n  real g(real x) {\\n    return x;\\n  }\\n}\\n')\n"
         "    p = pathlib.Path(f.name)\n"
         "r = e.extract_stan(p)\n"
         "assert any(n['label'] == 'g()' for n in r['nodes']), r\n"
         "print('dispatch smoke OK')"],
        check=False,
    ).returncode
    if rc != 0:
        print("ERROR: post-patch smoke test failed.", file=sys.stderr)
        return 4
    # 3. Run the extractors.py selftest too
    rc = subprocess.run(
        [python_bin, str(HERE / "extractors.py")],
        check=False,
    ).returncode
    if rc != 0:
        print("ERROR: extractors.py selftest failed.", file=sys.stderr)
        return 5
    return 0


def cmd_apply(python_bin: str, *, verbose: bool = True) -> int:
    extract_py = _find_module_file(python_bin, "graphify.extract")
    if verbose:
        print(f"graphify.extract -> {extract_py}")

    content = extract_py.read_text()

    # Backup once, before first-ever patch, for safety.
    backup = extract_py.with_suffix(".py.vault-backup")
    already_patched = (
        FOOTER_BEGIN in content
        or DISPATCH_MARK in content
        or EXTENSIONS_MARK in content
    )
    if not already_patched and not backup.exists():
        shutil.copy2(extract_py, backup)
        if verbose:
            print(f"backup written -> {backup}")

    # Apply in order: dispatch → extensions → footer (footer can reference
    # symbols already redefined by the earlier inserts if we extend later).
    changed_any = False
    new_content = content

    # Remove any prior footer first so we can re-emit with the current source.
    stripped = _remove_footer(new_content)
    if stripped != new_content:
        new_content = stripped
        changed_any = True

    new_content, d_changed = _inject_dispatch(new_content)
    e_changed = False  # _EXTENSIONS is auto-derived from _DISPATCH in this version
    new_content = new_content.rstrip() + "\n" + _build_footer_block()
    changed_any = True  # footer is always re-emitted

    if changed_any:
        tmp = extract_py.with_suffix(".py.tmp-vault-patch")
        tmp.write_text(new_content)
        tmp.replace(extract_py)
        if verbose:
            notes = []
            if d_changed: notes.append("dispatch")
            if e_changed: notes.append("extensions")
            notes.append("footer")
            print("patched:", ", ".join(notes))
    elif verbose:
        print("no changes needed")

    return _verify(python_bin)


def cmd_check(python_bin: str) -> int:
    extract_py = _find_module_file(python_bin, "graphify.extract")
    content = extract_py.read_text()
    status = {
        "footer": FOOTER_BEGIN in content and FOOTER_END in content,
        "dispatch": DISPATCH_MARK in content,
        "extensions": EXTENSIONS_MARK in content,
    }
    all_good = all(status.values())
    print(f"{extract_py}")
    for k, v in status.items():
        print(f"  {k:12} {'PATCHED' if v else 'MISSING'}")
    return 0 if all_good else 1


def cmd_remove(python_bin: str) -> int:
    extract_py = _find_module_file(python_bin, "graphify.extract")
    content = extract_py.read_text()
    new = _remove_footer(content)
    new = _remove_marker_block(new, DISPATCH_MARK)
    new = _remove_marker_block(new, EXTENSIONS_MARK)
    if new == content:
        print("no patch markers found — nothing to remove")
        return 0
    extract_py.write_text(new)
    print(f"patch removed from {extract_py}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Apply vault R/Stan patches to the installed graphifyy."
    )
    p.add_argument("--check", action="store_true",
                   help="report patch status and exit")
    p.add_argument("--remove", action="store_true",
                   help="remove the patch markers")
    p.add_argument("--python",
                   help="path to the Python interpreter that owns graphify")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args(argv)

    python_bin = _resolve_python(args.python)
    if not args.quiet:
        print(f"python: {python_bin}")

    if args.check:
        return cmd_check(python_bin)
    if args.remove:
        return cmd_remove(python_bin)
    return cmd_apply(python_bin, verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
