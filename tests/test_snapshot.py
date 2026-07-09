"""Regression tests for snapshot.py."""

from src.utils.snapshot import _should_ignore


def test_should_ignore_exact_match():
    assert _should_ignore(".DS_Store", ".DS_Store") is True
    assert _should_ignore("settings.local.json", "settings.local.json") is True
    assert _should_ignore("other.json", "settings.local.json") is False


def test_should_ignore_directory_prefix():
    assert _should_ignore(".github/workflows/ci.yml", ".github/") is True
    assert _should_ignore(".git/config", ".git/") is True
    assert _should_ignore("tests/test_sample.py", "tests/") is True


def test_should_ignore_does_not_overmatch():
    assert _should_ignore(".github-pages/foo.yml", ".github/") is False
    assert _should_ignore("tests_helper.py", "tests/") is False
    assert _should_ignore(".gitignore", ".git/") is False
