"""Helpers for matching ignore patterns against relative POSIX paths."""

from __future__ import annotations

import fnmatch
from typing import Iterable


def is_ignored(rel_posix: str, pattern: str) -> bool:
    """Return True when ``rel_posix`` matches a single ignore pattern."""
    if not isinstance(pattern, str):
        return False

    pat = pattern.strip()
    if not pat or pat.startswith("#"):
        return False

    if pat.endswith("/"):
        pat = pat.rstrip("/")

    if "/" not in pat:
        return any(fnmatch.fnmatchcase(part, pat) for part in rel_posix.split("/"))

    if fnmatch.fnmatchcase(rel_posix, pat):
        return True
    if rel_posix == pat:
        return True

    root_prefix = pat.rstrip("*").rstrip("/")
    if root_prefix and rel_posix.startswith(f"{root_prefix}/"):
        return True

    if fnmatch.fnmatchcase(rel_posix, pat.rstrip("/") + "/*"):
        return True

    return False


def matches_any(rel_posix: str, patterns: Iterable[str]) -> bool:
    """Return True if any ignore pattern matches ``rel_posix``."""
    return any(is_ignored(rel_posix, pattern) for pattern in patterns)
