#!/usr/bin/env bash
# Wrapper that picks the correct Python interpreter for the installed
# graphifyy and runs apply.py. Mirrors the detection in the graphify skill
# (SKILL.md step 1) so automated post-upgrade runs don't need any env
# plumbing.
#
# Usage:
#   ./apply.sh                 # apply the patches
#   ./apply.sh --check         # report patch status
#   ./apply.sh --remove        # strip the patches
#
# Exit codes propagate from apply.py (0 = ok, non-zero = failure).

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# 1. uv tool (preferred on modern setups)
PYTHON=""
if command -v uv >/dev/null 2>&1; then
    _UV_PY="$(uv tool run graphifyy python -c 'import sys; print(sys.executable)' 2>/dev/null || true)"
    if [ -n "$_UV_PY" ]; then PYTHON="$_UV_PY"; fi
fi

# 2. pipx / direct pip — read shebang from the graphify bin
if [ -z "$PYTHON" ]; then
    GRAPHIFY_BIN="$(command -v graphify 2>/dev/null || true)"
    if [ -n "$GRAPHIFY_BIN" ]; then
        _SHEBANG="$(head -1 "$GRAPHIFY_BIN" | tr -d '#!' | tr -d '[:space:]')"
        case "$_SHEBANG" in
            *[!a-zA-Z0-9/_.-]*) ;;  # reject suspicious chars
            *) if "$_SHEBANG" -c 'import graphify' 2>/dev/null; then
                   PYTHON="$_SHEBANG"
               fi ;;
        esac
    fi
fi

# 3. Fall back to system python3
if [ -z "$PYTHON" ]; then
    PYTHON="python3"
fi

# Ensure the target interpreter can import graphify; install graphifyy if not.
if ! "$PYTHON" -c 'import graphify' 2>/dev/null; then
    echo "graphifyy not importable in $PYTHON — attempting install..." >&2
    "$PYTHON" -m pip install graphifyy -q \
        || "$PYTHON" -m pip install graphifyy -q --break-system-packages \
        || {
            echo "ERROR: could not install graphifyy. Install it yourself and retry." >&2
            exit 10
        }
fi

exec "$PYTHON" "$HERE/apply.py" --python "$PYTHON" "$@"
