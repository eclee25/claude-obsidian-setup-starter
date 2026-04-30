#!/usr/bin/env python3
"""
claude_to_obsidian.py

Processes exported Claude chat markdown files and imports them into an Obsidian vault.

For each exported .md file:
  - Detects origin (Claude Code vs Claude Web)
  - Generates automatic tags from content keywords
  - Adds standardized YAML frontmatter
  - Inserts [[wikilinks]] for notes that already exist in the vault
  - Copies/moves to chats/code/ or chats/web/ inside the vault

Usage:
    python3 claude_to_obsidian.py \\
        --export-dir ~/claude-exports \\
        --vault-dir ~/vault \\
        [--move] \\
        [--dry-run]
"""

import argparse
import hashlib
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Keyword → tag mapping. Extend this to match your own stack / vocabulary.
# ---------------------------------------------------------------------------
KEYWORD_TAG_MAP: dict[str, str] = {
    # Languages
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "react": "react",
    "vue": "vue",
    "svelte": "svelte",
    "golang": "go",
    " go ": "go",
    "rust": "rust",
    "java": "java",
    "kotlin": "kotlin",
    "swift": "swift",
    "ruby": "ruby",
    "php": "php",
    "c#": "csharp",
    "csharp": "csharp",
    # Backend / infra
    "fastapi": "fastapi",
    "django": "django",
    "flask": "flask",
    "express": "express",
    "nextjs": "nextjs",
    "next.js": "nextjs",
    "supabase": "supabase",
    "postgres": "postgres",
    "postgresql": "postgres",
    "mysql": "mysql",
    "sqlite": "sqlite",
    "mongodb": "mongodb",
    "redis": "redis",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "terraform": "terraform",
    "aws": "aws",
    "gcp": "gcp",
    "azure": "azure",
    # Concepts
    "deploy": "deploy",
    "deployment": "deploy",
    "bug": "debugging",
    "debug": "debugging",
    "refactor": "refactoring",
    "refactoring": "refactoring",
    "api": "api",
    "auth": "auth",
    "authentication": "auth",
    "authorization": "auth",
    "test": "testing",
    "testing": "testing",
    "ci/cd": "cicd",
    "github actions": "cicd",
    "graphql": "graphql",
    "rest": "rest",
    "websocket": "websocket",
    "machine learning": "ml",
    "deep learning": "ml",
    "llm": "llm",
    "claude": "claude",
    "openai": "openai",
    "obsidian": "obsidian",
    "graphify": "graphify",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert arbitrary text to a safe kebab-case filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80]  # cap length


def file_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def detect_origin(filepath: Path, export_dir: Path) -> str:
    """
    Return 'code' or 'web' based on which sub-folder the file lives in
    relative to the export root.  Falls back to content heuristics.
    """
    try:
        relative = filepath.relative_to(export_dir)
        parts = relative.parts
        if parts and parts[0] == "code":
            return "code"
        if parts and parts[0] == "web":
            return "web"
    except ValueError:
        pass

    # Heuristic: Claude Code transcripts tend to mention terminal / bash blocks
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if "```bash" in content or "```shell" in content or "claude code" in content.lower():
        return "code"
    return "web"


def extract_title(content: str, fallback: str) -> str:
    """Try to pull a meaningful title from the first H1 or H2 heading."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# ") and len(line) > 2:
            return line[2:].strip()
        if line.startswith("## ") and len(line) > 3:
            return line[3:].strip()
    return fallback


def extract_date(content: str, filepath: Path) -> str:
    """
    Return ISO date string.  Prefer a date found in the content or filename;
    fall back to file mtime.
    """
    snippet = content[:500]
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", snippet)
    if m:
        return m.group(1)

    m = re.search(r"(\d{4}-\d{2}-\d{2})", filepath.stem)
    if m:
        return m.group(1)

    mtime = filepath.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def generate_tags(content: str) -> list[str]:
    """Scan content for keywords and return a deduplicated list of tags."""
    lower = content.lower()
    tags: set[str] = {"chat-import"}
    for keyword, tag in KEYWORD_TAG_MAP.items():
        if keyword in lower:
            tags.add(tag)
    return sorted(tags)


def collect_vault_note_names(vault_dir: Path, exclude_dirs: set[str]) -> set[str]:
    """
    Walk the vault and collect every note stem that is NOT inside the
    excluded sub-directories (chats, graphify) to avoid circular links.
    Returns stems in lowercase for case-insensitive matching.
    """
    names: set[str] = set()
    for md_file in vault_dir.rglob("*.md"):
        try:
            relative = md_file.relative_to(vault_dir)
        except ValueError:
            continue
        if relative.parts[0] in exclude_dirs:
            continue
        names.add(md_file.stem.lower())
    return names


def inject_wikilinks(content: str, vault_note_names: set[str]) -> str:
    """
    Replace plain occurrences of vault note names (that aren't already
    wikilinked or inside code blocks) with [[name]] wikilinks.
    """
    parts = re.split(r"(```[\s\S]*?```|`[^`]+`)", content)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            result.append(part)
        else:
            for name in sorted(vault_note_names, key=len, reverse=True):
                pattern = r"(?<!\[\[)\b" + re.escape(name) + r"\b(?!\]\])"
                replacement = f"[[{name}]]"
                part = re.sub(pattern, replacement, part, flags=re.IGNORECASE)
            result.append(part)
    return "".join(result)


def strip_existing_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block if the file already has one."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


def build_frontmatter(
    title: str,
    date: str,
    tags: list[str],
    origin: str,
    source_file: str,
) -> str:
    tags_yaml = "\n".join(f"  - {t}" for t in tags)
    return (
        f"---\n"
        f"title: \"{title}\"\n"
        f"tags:\n{tags_yaml}\n"
        f"created: {date}\n"
        f"updated: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"status: active\n"
        f"type: chat\n"
        f"chat-origin: {origin}\n"
        f"source-file: {source_file}\n"
        f"---\n\n"
    )


def unique_dest(dest: Path) -> Path:
    """If dest already exists, append a counter suffix."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    parent = dest.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


# ---------------------------------------------------------------------------
# Core processor
# ---------------------------------------------------------------------------

def process_file(
    filepath: Path,
    export_dir: Path,
    vault_dir: Path,
    vault_note_names: set[str],
    move: bool,
    dry_run: bool,
) -> dict:
    """Process a single exported markdown file and write it to the vault."""
    result = {"file": str(filepath), "status": "ok", "dest": None, "message": ""}

    try:
        raw_content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        result.update({"status": "error", "message": str(e)})
        return result

    origin = detect_origin(filepath, export_dir)
    date = extract_date(raw_content, filepath)
    body = strip_existing_frontmatter(raw_content)
    title = extract_title(body, filepath.stem.replace("-", " ").replace("_", " ").title())
    tags = generate_tags(body)
    body_with_links = inject_wikilinks(body, vault_note_names)
    frontmatter = build_frontmatter(title, date, tags, origin, filepath.name)
    final_content = frontmatter + body_with_links

    dest_subdir = vault_dir / "chats" / origin
    safe_stem = slugify(title) or slugify(filepath.stem)
    dest_name = f"{date}-{safe_stem}.md"
    dest = unique_dest(dest_subdir / dest_name)
    result["dest"] = str(dest)

    if dry_run:
        result["status"] = "dry-run"
        result["message"] = f"Would write to {dest}"
        return result

    dest_subdir.mkdir(parents=True, exist_ok=True)
    dest.write_text(final_content, encoding="utf-8")

    if move:
        filepath.unlink()
        result["message"] = "moved"
    else:
        result["message"] = "copied"

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import exported Claude chats into an Obsidian vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--export-dir",
        required=True,
        type=Path,
        help="Root directory of exported chats (contains code/ and web/ sub-dirs).",
    )
    parser.add_argument(
        "--vault-dir",
        required=True,
        type=Path,
        help="Root directory of the Obsidian vault.",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Delete the source file after successful import (default: copy only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without writing anything.",
    )
    parser.add_argument(
        "--no-wikilinks",
        action="store_true",
        help="Skip wikilink injection (faster for large vaults).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print per-file details.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    export_dir: Path = args.export_dir.expanduser().resolve()
    vault_dir: Path = args.vault_dir.expanduser().resolve()

    if not export_dir.is_dir():
        print(f"[ERROR] export-dir not found: {export_dir}", file=sys.stderr)
        return 1
    if not vault_dir.is_dir():
        print(f"[ERROR] vault-dir not found: {vault_dir}", file=sys.stderr)
        return 1

    print("[info] Scanning vault for existing note names…")
    vault_note_names: set[str] = set()
    if not args.no_wikilinks:
        vault_note_names = collect_vault_note_names(
            vault_dir,
            exclude_dirs={"chats", "graphify"},
        )
        print(f"[info] Found {len(vault_note_names)} existing notes for wikilink matching.")

    md_files = list(export_dir.rglob("*.md"))
    if not md_files:
        print("[info] No markdown files found in export-dir. Nothing to do.")
        return 0

    print(f"[info] Processing {len(md_files)} file(s)…")

    stats = {"ok": 0, "error": 0, "dry-run": 0}

    for filepath in sorted(md_files):
        res = process_file(
            filepath=filepath,
            export_dir=export_dir,
            vault_dir=vault_dir,
            vault_note_names=vault_note_names,
            move=args.move,
            dry_run=args.dry_run,
        )
        stats[res["status"]] = stats.get(res["status"], 0) + 1

        if args.verbose or res["status"] == "error":
            icon = {"ok": "+", "error": "x", "dry-run": "~"}.get(res["status"], "?")
            print(f"  {icon} {res['file']}")
            if res["dest"]:
                print(f"      -> {res['dest']}")
            if res["message"] and args.verbose:
                print(f"      {res['message']}")

    print(
        f"\n[done] Processed {len(md_files)} file(s): "
        f"{stats.get('ok', 0)} imported, "
        f"{stats.get('error', 0)} errors, "
        f"{stats.get('dry-run', 0)} dry-run."
    )
    return 0 if stats.get("error", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
