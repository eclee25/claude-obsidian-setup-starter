#!/bin/bash
# sync_claude_obsidian.sh
# Run by the Claude Code Stop hook after every session.
# Extracts sessions from each Claude profile and lands them in the vault as
# enriched markdown via claude_to_obsidian.py.
#
# Configure via env vars or edit the defaults below. The script is idempotent
# and safe to re-run manually.

set -u
export PATH="$HOME/.local/bin:$PATH"

# --- Paths (override via env) ----------------------------------------------
EXPORT_DIR="${CLAUDE_EXPORT_DIR:-$HOME/claude-exports}"
VAULT_DIR="${CLAUDE_VAULT_DIR:-$HOME/vault}"
SCRIPT_DIR="${CLAUDE_SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
LOG="${CLAUDE_SYNC_LOG:-$SCRIPT_DIR/sync.log}"

# Profiles to extract from. Add or remove entries to match your setup.
PROFILES=("${CLAUDE_PROFILES[@]:-.claude .claude-perso .claude-gdd}")

mkdir -p "$EXPORT_DIR/code"

echo "[$(date)] Sync started" >> "$LOG"

# --- Extract from every profile that exists --------------------------------
for PROFILE in "${PROFILES[@]}"; do
    CONFIG_DIR="$HOME/$PROFILE"
    if [ -d "$CONFIG_DIR/sessions" ]; then
        echo "[$(date)] Extracting from $PROFILE" >> "$LOG"
        CLAUDE_CONFIG_DIR="$CONFIG_DIR" \
            claude-extract --all --output "$EXPORT_DIR/code" 2>> "$LOG"
    fi
done

# --- Process and import into the vault -------------------------------------
python3 "$SCRIPT_DIR/claude_to_obsidian.py" \
    --export-dir "$EXPORT_DIR" \
    --vault-dir "$VAULT_DIR" \
    --move 2>> "$LOG"

echo "[$(date)] Sync completed" >> "$LOG"
