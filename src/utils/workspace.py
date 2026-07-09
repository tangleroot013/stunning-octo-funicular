import fnmatch
import pathlib
from typing import Iterable, List

from src.utils.config_loader import settings


def load_exclude_patterns() -> List[str]:
    """Load claude-ignore exclude globs from settings, with fallback.

    Prefers workspace.ignore_patterns.claudeignore, falling back to
    ai_collaboration.directory_scanning_protection.exclude_globs.
    """
    patterns = settings.get("workspace.ignore_patterns.claudeignore")
    if not patterns:
        patterns = settings.get(
            "ai_collaboration.directory_scanning_protection.exclude_globs", []
        )
    if not isinstance(patterns, list):
        patterns = []
    return patterns


def matches_any(rel_path: pathlib.Path, patterns: Iterable[str]) -> bool:
    """True if the POSIX form of rel_path fnmatches any pattern."""
    path_str = rel_path.as_posix()
    return any(fnmatch.fnmatch(path_str, pat) for pat in patterns)
