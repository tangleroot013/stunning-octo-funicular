"""
Synchronize .claudeignore and .gitignore from settings.json.

This module keeps ignore patterns in a single source of truth (settings.json)
and propagates them to both .claudeignore and .gitignore, preventing drift.
"""

from __future__ import annotations

import pathlib
import sys
from typing import Any, Iterable, List, Optional, Set, Tuple

from src.utils.config_loader import settings


class SyncIgnoresError(Exception):
    """Raised when ignore-file synchronization cannot complete."""


# Sensible defaults for generated projects. Users can override these in
# settings.json under workspace.ignore_patterns.
DEFAULT_CLAUDEIGNORE_PATTERNS: List[str] = [
    ".git/",
    ".github/",
    ".gitignore",
    ".gitattributes",
    ".gitmessage",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "Pipfile.lock",
    "node_modules/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".venv/",
    "venv/",
    "env/",
    "build/",
    "dist/",
    "*.egg-info/",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    ".tox/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".idea/",
    ".vscode/",
    ".DS_Store",
    "*.log",
    "tests/",
    "tests/**",
    "docs/",
    "docs/**",
    "settings.local.json",
    "secrets.env",
    ".env",
    ".env.*",
    "*.local",
    "project_snapshot.md",
]

DEFAULT_GITIGNORE_PATTERNS: List[str] = [
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".venv/",
    "venv/",
    "env/",
    "build/",
    "dist/",
    "*.egg-info/",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    ".tox/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".idea/",
    ".vscode/",
    ".DS_Store",
    "*.log",
    "node_modules/",
    ".env",
    ".env.*",
    "*.local",
    "settings.local.json",
    "secrets.env",
]

# .gitignore entries that must never be removed, even when merging.
CRITICAL_GITIGNORE_ENTRIES: Set[str] = {
    ".env",
    ".env.*",
    "*.local",
    "settings.local.json",
    "secrets.env",
    ".DS_Store",
}


def _resolve_root(start: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Locate the repository root.

    If ``start`` is provided, use it. Otherwise search upward for a .git
    directory, falling back to the directory containing this source file.
    """
    if start is not None:
        return start.resolve()

    current = pathlib.Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").is_dir():
            return parent

    # Fallback: src/utils/sync_ignores.py is two levels below the repo root.
    return current.parents[2]


def _validate_patterns(patterns: Any) -> List[str]:
    """Ensure ``patterns`` is a list of non-empty strings."""
    if patterns is None:
        return []
    if not isinstance(patterns, list):
        raise SyncIgnoresError(
            f"ignore patterns must be a list, got {type(patterns).__name__}"
        )

    cleaned: List[str] = []
    for idx, pattern in enumerate(patterns):
        if not isinstance(pattern, str):
            raise SyncIgnoresError(
                f"ignore pattern at index {idx} is not a string: {pattern!r}"
            )
        pattern = pattern.strip()
        if pattern:
            cleaned.append(pattern)
    return cleaned


def _read_ignore_file(path: pathlib.Path) -> List[str]:
    """Read an existing ignore file, preserving order and skipping comments/blanks."""
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SyncIgnoresError(f"failed to read {path}: {exc}") from exc

    seen: Set[str] = set()
    ordered: List[str] = []
    for line in lines:
        pattern = line.strip()
        if pattern and not pattern.startswith("#") and pattern not in seen:
            seen.add(pattern)
            ordered.append(pattern)
    return ordered


def _write_ignore_file(
    path: pathlib.Path,
    patterns: Iterable[str],
    preserve_existing: bool = False,
) -> int:
    """Write ``patterns`` to ``path``, optionally merging with existing lines.

    For ``.gitignore`` the existing file order is preserved so negation
    patterns continue to work correctly. Missing patterns and critical
    security entries are appended at the end. ``.claudeignore`` is sorted
    alphabetically because order has no special meaning for that file.

    Returns the number of lines written.
    """
    new_patterns = [p for p in patterns if isinstance(p, str) and p.strip()]

    if path.name == ".gitignore" and preserve_existing:
        # Preserve existing order, then append new/critical patterns.
        existing = _read_ignore_file(path)
        ordered: List[str] = []
        seen: Set[str] = set()
        for p in existing + new_patterns:
            if p not in seen:
                seen.add(p)
                ordered.append(p)
        for p in CRITICAL_GITIGNORE_ENTRIES:
            if p not in seen:
                seen.add(p)
                ordered.append(p)
    else:
        merged = set(new_patterns)
        if path.name == ".gitignore":
            merged |= CRITICAL_GITIGNORE_ENTRIES
        elif path.name == ".claudeignore":
            merged.discard(".claudeignore")
        ordered = sorted(merged)

    content = "\n".join(ordered) + "\n" if ordered else "\n"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise SyncIgnoresError(f"failed to write {path}: {exc}") from exc

    return len(ordered)


def _load_patterns() -> Tuple[List[str], List[str]]:
    """Load .claudeignore and .gitignore patterns from settings.json."""
    settings.load()

    workspace_patterns = settings.get("workspace.ignore_patterns", {})
    claude_patterns = _validate_patterns(
        workspace_patterns.get("claudeignore")
        if isinstance(workspace_patterns, dict)
        else None
    )
    git_patterns = _validate_patterns(
        workspace_patterns.get("gitignore")
        if isinstance(workspace_patterns, dict)
        else None
    )

    # Fall back to defaults when the user has not configured explicit patterns.
    if not claude_patterns:
        claude_patterns = _validate_patterns(
            settings.get("ai_collaboration.directory_scanning_protection.exclude_globs", [])
        )
    if not claude_patterns:
        claude_patterns = DEFAULT_CLAUDEIGNORE_PATTERNS.copy()

    if not git_patterns:
        git_patterns = DEFAULT_GITIGNORE_PATTERNS.copy()

    return claude_patterns, git_patterns


def sync_ignore_files(
    root_dir: Optional[pathlib.Path] = None,
    verbose: bool = False,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """Synchronize .claudeignore and .gitignore from settings.json.

    Args:
        root_dir: Project root to write files into. Defaults to repo root.
        verbose: Print progress messages.
        dry_run: Do not write files; only report what would change.

    Returns:
        A (success, message) tuple.
    """
    try:
        repo_root = _resolve_root(root_dir)
    except SyncIgnoresError as exc:
        return False, f"Error: {exc}"

    try:
        claude_patterns, git_patterns = _load_patterns()
    except SyncIgnoresError as exc:
        return False, f"Error: {exc}"

    if not claude_patterns and not git_patterns:
        return False, "No ignore patterns found in settings.json"

    claude_path = repo_root / ".claudeignore"
    git_path = repo_root / ".gitignore"

    if dry_run:
        summary = (
            f"Dry run: would write {len(claude_patterns)} patterns to {claude_path}\n"
            f"and {len(git_patterns)} patterns to {git_path}"
        )
        if verbose:
            print(summary)
        return True, summary

    try:
        claude_count = _write_ignore_file(
            claude_path, claude_patterns, preserve_existing=False
        )
        git_count = _write_ignore_file(
            git_path, git_patterns, preserve_existing=True
        )
    except SyncIgnoresError as exc:
        return False, f"Error: {exc}"

    msg = (
        f"Synchronized ignore files: "
        f".claudeignore={claude_count}, .gitignore={git_count}"
    )

    if verbose:
        print(f"Repository root: {repo_root}")
        print(f"Wrote {claude_count} patterns to {claude_path}")
        print(f"Wrote {git_count} patterns to {git_path}")

    return True, msg


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for manual syncing."""
    argv = argv or sys.argv[1:]
    verbose = "-v" in argv or "--verbose" in argv
    dry_run = "--dry-run" in argv
    root = pathlib.Path(".") if "--root" not in argv else None
    # A real --root parser is overkill here; sync from CWD if requested.
    if "--root" in argv:
        try:
            idx = argv.index("--root")
            root = pathlib.Path(argv[idx + 1]).resolve()
        except (IndexError, ValueError):
            print("Error: --root requires a path", file=sys.stderr)
            return 1

    success, message = sync_ignore_files(
        root_dir=root, verbose=verbose, dry_run=dry_run
    )
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
