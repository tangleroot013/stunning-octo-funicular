"""Tests for shared ignore-pattern matching."""

import pytest

from src.utils.ignore_match import is_ignored, matches_any


@pytest.mark.parametrize(
    ("rel_posix", "patterns"),
    [
        (".env", [".env"]),
        ("sub/.env", [".env"]),
        ("production.local", ["*.local"]),
        ("nested/production.local", ["*.local"]),
        ("secrets.env", ["secrets.env"]),
        ("sub/settings.local.json", ["settings.local.json"]),
        ("tests/test_app.py", ["tests/**"]),
        ("docs/guide/index.md", ["docs/"]),
        (".claudeignore", [".claudeignore"]),
    ],
)
def test_ignore_patterns_match_sensitive_or_noisy_paths(rel_posix, patterns):
    assert matches_any(rel_posix, patterns) is True


@pytest.mark.parametrize(
    ("rel_posix", "patterns"),
    [
        ("src/utils/snapshot.py", [".env", "*.local", "tests/**", "docs/"]),
        (".claudeignore", [".env", "*.local", "tests/**", "docs/"]),
    ],
)
def test_normal_files_and_claudeignore_are_not_excluded_by_unrelated_patterns(
    rel_posix, patterns
):
    assert matches_any(rel_posix, patterns) is False


def test_is_ignored_skips_comments_and_empty_patterns():
    assert is_ignored("src/utils/snapshot.py", "") is False
    assert is_ignored("src/utils/snapshot.py", "   ") is False
    assert is_ignored("src/utils/snapshot.py", "# comment") is False
