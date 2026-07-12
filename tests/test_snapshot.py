"""Tests for src/utils/snapshot.py — closes coverage gaps at lines
11, 16, 20-29, 55-68, 85-89, 93."""
import sys
import pathlib
import pytest

from src.utils import snapshot


class FakeSettings:
    """Minimal stand-in for src.utils.config_loader.settings."""
    def __init__(self, values=None):
        self.values = values or {}

    def get(self, key, default=None):
        return self.values.get(key, default)


@pytest.fixture
def project_tree(tmp_path):
    (tmp_path / "keep.py").write_text("print('hello')")
    (tmp_path / "skip_dir").mkdir()
    (tmp_path / "skip_dir" / "ignored.py").write_text("print('ignored')")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested.py").write_text("print('nested')")
    return tmp_path


def test_iter_project_files_falls_back_to_ai_collaboration_globs(project_tree, monkeypatch):
    """Line 11: when claudeignore patterns are empty, fall back to the
    ai_collaboration.directory_scanning_protection.exclude_globs key."""
    fake = FakeSettings({
        "workspace.ignore_patterns.claudeignore": [],
        "ai_collaboration.directory_scanning_protection.exclude_globs": ["skip_dir"],
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    files = snapshot._iter_project_files(project_tree)
    names = {f.relative_to(project_tree).as_posix() for f in files}

    assert "keep.py" in names
    assert "subdir/nested.py" in names
    assert "skip_dir/ignored.py" not in names


def test_iter_project_files_resets_non_list_exclude_globs(project_tree, monkeypatch):
    """Line 16: a non-list exclude_globs value is coerced to an empty list
    instead of crashing the `any(...)` filter."""
    fake = FakeSettings({
        "workspace.ignore_patterns.claudeignore": "not-a-list",
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    files = snapshot._iter_project_files(project_tree)
    names = {f.relative_to(project_tree).as_posix() for f in files}

    # nothing should be excluded since the bad value was reset to []
    assert "skip_dir/ignored.py" in names


def test_iter_project_files_skips_directories(project_tree, monkeypatch):
    """Lines 20-21: directories themselves (not just their files) are
    skipped by the is_file() check."""
    fake = FakeSettings({})
    monkeypatch.setattr(snapshot, "settings", fake)

    files = snapshot._iter_project_files(project_tree)
    for f in files:
        assert f.is_file()


def test_build_context_snapshot_handles_unreadable_file(project_tree, monkeypatch):
    """Lines 57-59: a file that raises UnicodeDecodeError/OSError on read
    is included with empty content instead of crashing the build."""
    bad_file = project_tree / "binary.dat"
    bad_file.write_bytes(b"\xff\xfe\x00\x01")

    fake = FakeSettings({
        "ai_collaboration.byte_budget.max_bytes_per_file": 51_200,
        "ai_collaboration.byte_budget.total_payload_limit_bytes": 1_048_576,
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    out = snapshot.build_context_snapshot(project_tree)
    assert out.exists()
    out.unlink()


def test_build_context_snapshot_truncates_large_file(project_tree, monkeypatch):
    """Lines 61-63: a file exceeding max_bytes_per_file gets truncated
    with a `[truncated]` marker."""
    big_file = project_tree / "big.py"
    big_file.write_text("x" * 200)

    fake = FakeSettings({
        "ai_collaboration.byte_budget.max_bytes_per_file": 50,
        "ai_collaboration.byte_budget.total_payload_limit_bytes": 1_048_576,
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    out = snapshot.build_context_snapshot(project_tree)
    text = out.read_text()
    assert "[truncated]" in text
    out.unlink()


def test_build_context_snapshot_respects_total_payload_limit(project_tree, monkeypatch):
    """Lines 64-65: once total_payload_limit_bytes is exceeded, remaining
    files are skipped via the break."""
    for i in range(5):
        (project_tree / f"file_{i}.py").write_text("y" * 100)

    fake = FakeSettings({
        "ai_collaboration.byte_budget.max_bytes_per_file": 1000,
        "ai_collaboration.byte_budget.total_payload_limit_bytes": 150,
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    out = snapshot.build_context_snapshot(project_tree)
    text = out.read_text()
    # not every file should have made it in, given the tiny payload limit
    included = text.count("### file_")
    assert included < 5
    out.unlink()


def test_build_context_snapshot_writes_expected_sections(project_tree, monkeypatch):
    """Lines 40-51: header/overview sections are populated from settings."""
    fake = FakeSettings({
        "repository.name": "test-repo",
        "ai_collaboration.target_assistant": "TestBot",
        "ai_collaboration.custom_personas.default": "engineer",
    })
    monkeypatch.setattr(snapshot, "settings", fake)

    out = snapshot.build_context_snapshot(project_tree)
    text = out.read_text()

    assert "test-repo" in text
    assert "TestBot" in text
    assert "engineer" in text
    out.unlink()


def test_main_invokes_build_and_prints(project_tree, monkeypatch, capsys):
    """Lines 85-89: the CLI entrypoint parses --root, builds the snapshot,
    and prints the output path."""
    fake = FakeSettings({})
    monkeypatch.setattr(snapshot, "settings", fake)
    monkeypatch.setattr(sys, "argv", ["snapshot.py", "--root", str(project_tree)])

    snapshot.main()

    captured = capsys.readouterr()
    assert "Snapshot written to" in captured.out
    (project_tree / "project_snapshot.md").unlink(missing_ok=True)
