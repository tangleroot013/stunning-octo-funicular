"""Unit tests for snapshot.py (project context snapshot generation)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.utils import snapshot
from src.utils.snapshot import (
    _iter_project_files,
    build_context_snapshot,
    main,
)


def _stub_settings(monkeypatch, values):
    """Route snapshot.settings.get through a dict keyed by dotted path."""
    monkeypatch.setattr(
        snapshot.settings,
        "get",
        lambda key, default=None: values.get(key, default),
    )


# --------------------------------------------------------------------------
# _iter_project_files
# --------------------------------------------------------------------------


def test_iter_project_files_returns_sorted_files(tmp_path, monkeypatch):
    _stub_settings(monkeypatch, {})
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")

    files = _iter_project_files(tmp_path)

    assert [p.name for p in files] == ["a.txt", "b.txt"]


def test_iter_project_files_skips_directories(tmp_path, monkeypatch):
    _stub_settings(monkeypatch, {})
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.txt").write_text("x", encoding="utf-8")

    files = _iter_project_files(tmp_path)

    assert all(p.is_file() for p in files)
    assert [p.relative_to(tmp_path).as_posix() for p in files] == ["sub/nested.txt"]


def test_iter_project_files_excludes_matching_patterns(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {"workspace.ignore_patterns.claudeignore": ["secrets/", "top.txt"]},
    )
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "top.txt").write_text("drop", encoding="utf-8")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "key.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "secretsfile.txt").write_text("not secret", encoding="utf-8")

    rels = [p.relative_to(tmp_path).as_posix() for p in _iter_project_files(tmp_path)]

    assert rels == ["keep.txt", "secretsfile.txt"]


def test_iter_project_files_falls_back_to_exclude_globs(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {
            "workspace.ignore_patterns.claudeignore": None,
            "ai_collaboration.directory_scanning_protection.exclude_globs": ["drop.txt"],
        },
    )
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "drop.txt").write_text("drop", encoding="utf-8")

    rels = [p.relative_to(tmp_path).as_posix() for p in _iter_project_files(tmp_path)]

    assert rels == ["keep.txt"]


def test_iter_project_files_ignores_non_list_exclude_globs(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {"workspace.ignore_patterns.claudeignore": "not-a-list"},
    )
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")

    rels = [p.relative_to(tmp_path).as_posix() for p in _iter_project_files(tmp_path)]

    assert rels == ["a.txt"]


# --------------------------------------------------------------------------
# build_context_snapshot
# --------------------------------------------------------------------------


def test_build_context_snapshot_writes_overview_and_files(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {
            "repository.name": "my-repo",
            "ai_collaboration.target_assistant": "Carter",
            "ai_collaboration.custom_personas.default": "duck",
        },
    )
    (tmp_path / "hello.py").write_text("print('hi')", encoding="utf-8")

    output_path = build_context_snapshot(root_dir=tmp_path)

    assert output_path == tmp_path / "project_snapshot.md"
    content = output_path.read_text(encoding="utf-8")
    assert "# Project Context Snapshot" in content
    assert "- Repository: my-repo" in content
    assert "- Assistant: Carter" in content
    assert "- Persona: duck" in content
    assert "### hello.py" in content
    assert "print('hi')" in content
    assert content.endswith("\n")


def test_build_context_snapshot_truncates_large_files(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {"ai_collaboration.byte_budget.max_bytes_per_file": 10},
    )
    (tmp_path / "big.txt").write_text("x" * 100, encoding="utf-8")

    content = build_context_snapshot(root_dir=tmp_path).read_text(encoding="utf-8")

    assert "... [truncated]" in content


def test_build_context_snapshot_respects_total_payload_limit(tmp_path, monkeypatch):
    _stub_settings(
        monkeypatch,
        {
            "ai_collaboration.byte_budget.max_bytes_per_file": 51_200,
            "ai_collaboration.byte_budget.total_payload_limit_bytes": 5,
        },
    )
    (tmp_path / "a.txt").write_text("a" * 50, encoding="utf-8")
    (tmp_path / "b.txt").write_text("b" * 50, encoding="utf-8")

    content = build_context_snapshot(root_dir=tmp_path).read_text(encoding="utf-8")

    # Payload limit is exceeded by the first file, so no file bodies are emitted.
    assert "### a.txt" not in content
    assert "### b.txt" not in content


def test_build_context_snapshot_handles_unreadable_files(tmp_path, monkeypatch):
    _stub_settings(monkeypatch, {})
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"\xff\xfe\x00")

    # Should not raise despite the undecodable bytes.
    content = build_context_snapshot(root_dir=tmp_path).read_text(encoding="utf-8")

    assert "### bad.bin" in content


def test_build_context_snapshot_defaults_root_to_repo_root(tmp_path, monkeypatch):
    _stub_settings(monkeypatch, {})
    fake_snapshot = tmp_path / "src" / "utils" / "snapshot.py"
    fake_snapshot.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(snapshot, "__file__", str(fake_snapshot))
    monkeypatch.setattr(snapshot, "_iter_project_files", lambda root: [])

    output_path = build_context_snapshot()

    assert output_path == tmp_path / "project_snapshot.md"
    assert output_path.exists()


# --------------------------------------------------------------------------
# main / CLI
# --------------------------------------------------------------------------


def test_main_prints_output_path(tmp_path, monkeypatch, capsys):
    _stub_settings(monkeypatch, {})
    (tmp_path / "file.txt").write_text("data", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["snapshot", "--root", str(tmp_path)])

    main()

    captured = capsys.readouterr()
    assert "Snapshot written to" in captured.out
    assert (tmp_path / "project_snapshot.md").exists()
