"""Regression tests for sync_ignores.py."""

import pathlib
import subprocess
import sys
from unittest.mock import patch

import pytest

from src.utils import sync_ignores
from src.utils.sync_ignores import (
    DEFAULT_CLAUDEIGNORE_PATTERNS,
    DEFAULT_GITIGNORE_PATTERNS,
    SyncIgnoresError,
    _load_patterns,
    _resolve_root,
    _validate_patterns,
    _write_ignore_file,
    sync_ignore_files,
)


def test_resolve_root_uses_start_argument(tmp_path):
    assert _resolve_root(tmp_path) == tmp_path


def test_resolve_root_finds_git_directory(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    fake_module = tmp_path / "src" / "utils" / "sync_ignores.py"
    fake_module.parent.mkdir(parents=True)
    monkeypatch.setattr(sync_ignores, "__file__", str(fake_module))

    assert _resolve_root() == tmp_path


def test_validate_patterns_strips_and_filters_empty():
    assert _validate_patterns(["  a  ", "", "  ", "b"]) == ["a", "b"]


def test_validate_patterns_rejects_non_list():
    with pytest.raises(SyncIgnoresError, match="ignore patterns must be a list"):
        _validate_patterns("not-a-list")


def test_validate_patterns_rejects_non_string_elements():
    with pytest.raises(SyncIgnoresError, match="is not a string"):
        _validate_patterns(["ok", 123, "fine"])


def test_load_patterns_prefers_workspace_settings(monkeypatch):
    def fake_get(key, default=None):
        if key == "workspace.ignore_patterns":
            return {
                "claudeignore": ["claude/custom/"],
                "gitignore": ["git/custom/"],
            }
        if key == "ai_collaboration.directory_scanning_protection.exclude_globs":
            return ["fallback/"]
        return default

    monkeypatch.setattr(sync_ignores.settings, "load", lambda: None)
    monkeypatch.setattr(sync_ignores.settings, "get", fake_get)

    claude, git = _load_patterns()
    assert claude == ["claude/custom/"]
    assert git == ["git/custom/"]


def test_load_patterns_falls_back_to_exclude_globs(monkeypatch):
    monkeypatch.setattr(sync_ignores.settings, "load", lambda: None)
    monkeypatch.setattr(
        sync_ignores.settings,
        "get",
        lambda key, default=None: {
            "ai_collaboration.directory_scanning_protection.exclude_globs": ["ai-excluded/**"],
        }.get(key, default),
    )

    claude, git = _load_patterns()
    assert claude == ["ai-excluded/**"]
    assert git == DEFAULT_GITIGNORE_PATTERNS


def test_load_patterns_falls_back_to_defaults_when_empty(monkeypatch):
    monkeypatch.setattr(sync_ignores.settings, "load", lambda: None)
    monkeypatch.setattr(
        sync_ignores.settings,
        "get",
        lambda key, default=None: default,
    )

    claude, git = _load_patterns()
    assert claude == DEFAULT_CLAUDEIGNORE_PATTERNS
    assert git == DEFAULT_GITIGNORE_PATTERNS


def test_write_ignore_file_creates_claudeignore(tmp_path):
    target = tmp_path / ".claudeignore"
    _write_ignore_file(target, ["zebra/", "apple/", "zebra/"], preserve_existing=False)

    content = target.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    assert lines == ["apple/", "zebra/"]
    assert content.endswith("\n")


def test_write_ignore_file_preserves_critical_gitignore_entries(tmp_path):
    target = tmp_path / ".gitignore"
    target.write_text(".env\nbuild/\n", encoding="utf-8")

    _write_ignore_file(target, ["node_modules/"], preserve_existing=True)

    content = target.read_text(encoding="utf-8").strip().split("\n")
    assert ".env" in content
    assert "build/" in content
    assert "node_modules/" in content
    assert ".DS_Store" in content


def test_sync_ignore_files_writes_both_ignores(tmp_path):
    success, msg = sync_ignore_files(root_dir=tmp_path)
    assert success is True

    claude = tmp_path / ".claudeignore"
    git = tmp_path / ".gitignore"
    assert claude.exists()
    assert git.exists()

    claude_content = claude.read_text(encoding="utf-8")
    git_content = git.read_text(encoding="utf-8")
    assert claude_content
    assert git_content
    assert ".env" in git_content
    assert "__pycache__/" in git_content


def test_sync_ignore_files_dry_run_does_not_write(tmp_path):
    success, msg = sync_ignore_files(root_dir=tmp_path, dry_run=True)
    assert success is True
    assert "Dry run" in msg
    assert not (tmp_path / ".claudeignore").exists()
    assert not (tmp_path / ".gitignore").exists()


def test_sync_ignore_files_is_idempotent(tmp_path):
    sync_ignore_files(root_dir=tmp_path)
    first_claude = (tmp_path / ".claudeignore").read_text(encoding="utf-8")
    first_git = (tmp_path / ".gitignore").read_text(encoding="utf-8")

    sync_ignore_files(root_dir=tmp_path)
    second_claude = (tmp_path / ".claudeignore").read_text(encoding="utf-8")
    second_git = (tmp_path / ".gitignore").read_text(encoding="utf-8")

    assert first_claude == second_claude
    assert first_git == second_git


def test_sync_ignore_files_verbose_prints(tmp_path, capsys):
    success, _ = sync_ignore_files(root_dir=tmp_path, verbose=True)
    assert success is True
    captured = capsys.readouterr()
    assert str(tmp_path) in captured.out
    assert ".claudeignore" in captured.out
    assert ".gitignore" in captured.out


def test_hatch_sync_ignores_cli(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "hatch.py",
            "--sync-ignores",
            "--path",
            str(tmp_path),
        ],
        cwd=str(pathlib.Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Synchronized" in result.stdout
    assert (tmp_path / ".claudeignore").exists()
    assert (tmp_path / ".gitignore").exists()


def test_hatch_sync_ignores_cli_dry_run(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "hatch.py",
            "--sync-ignores",
            "--path",
            str(tmp_path),
            "--dry-run",
        ],
        cwd=str(pathlib.Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Dry run" in result.stdout
    assert not (tmp_path / ".claudeignore").exists()
    assert not (tmp_path / ".gitignore").exists()
