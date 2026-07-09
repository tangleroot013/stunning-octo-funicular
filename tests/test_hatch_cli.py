"""CLI-level tests for hatch.py entry points and argument handling."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import hatch


def test_cli_version(capsys):
    with patch.object(sys, "argv", ["hatch.py", "--version"]):
        with pytest.raises(SystemExit) as exc:
            hatch.main()
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "0.2.2" in captured.out


def test_cli_sync_ignores_dry_run(capsys):
    with patch.object(sys, "argv", ["hatch.py", "--sync-ignores", "--dry-run"]):
        with pytest.raises(SystemExit) as exc:
            hatch.main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "Dry run" in out


def test_cli_scaffold_uses_template_and_coverage_threshold(
    tmp_path, monkeypatch
):
    project_dir = tmp_path / "myproj"
    monkeypatch.setattr(hatch, "init_git_repo", lambda p: None)
    monkeypatch.setattr(hatch, "create_git_hook", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "create_git_message", lambda p, **kw: None)

    with patch.object(
        sys,
        "argv",
        [
            "hatch.py",
            "myproj",
            "-p",
            str(tmp_path),
            "-t",
            "cli",
            "--coverage-threshold",
            "92",
        ],
    ):
        hatch.main()

    assert (project_dir / "src" / "main.py").exists()
    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text()
    assert "pytest --cov . --cov-fail-under=92" in workflow


def test_cli_scaffold_defaults_to_standard_coverage_threshold(
    tmp_path, monkeypatch
):
    project_dir = tmp_path / "defaultcov"
    monkeypatch.setattr(hatch, "init_git_repo", lambda p: None)
    monkeypatch.setattr(hatch, "create_git_hook", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "create_git_message", lambda p, **kw: None)

    with patch.object(
        sys, "argv", ["hatch.py", "defaultcov", "-p", str(tmp_path)]
    ):
        hatch.main()

    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text()
    assert "pytest --cov . --cov-fail-under=85" in workflow


def test_cli_setup_global_installs_git_template(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)

    with patch.object(sys, "argv", ["hatch.py", "--setup-global"]):
        with pytest.raises(SystemExit) as exc:
            hatch.main()

    assert exc.value.code == 0
    assert (home / ".git-templates" / "hooks" / "pre-commit").exists()
    assert (home / ".gitmessage").exists()

    hook_text = (home / ".git-templates" / "hooks" / "pre-commit").read_text()
    assert "{hooks}" not in hook_text
    assert "py_compile" in hook_text or "secret" in hook_text.lower()


def test_cli_wizard_forwards_flags_to_scaffold(tmp_path, monkeypatch):
    captured = {}

    def fake_scaffold(project_name, base_path, template, coverage_threshold=85):
        captured.update(
            {
                "project_name": project_name,
                "base_path": base_path,
                "template": template,
                "coverage_threshold": coverage_threshold,
            }
        )
        return tmp_path / project_name

    monkeypatch.setattr(hatch, "scaffold", fake_scaffold)
    monkeypatch.setattr(
        hatch,
        "collect_answers",
        lambda defaults=None: {
            "project_name": "wizard-proj",
            "template": defaults.get("template") if defaults else "cli",
            "base_path": defaults.get("base_path") if defaults else ".",
            "coverage_threshold": defaults.get("coverage_threshold", 85)
            if defaults
            else 85,
            "setup_global": False,
        },
    )

    with patch.object(
        sys,
        "argv",
        [
            "hatch.py",
            "-t",
            "web",
            "-p",
            str(tmp_path),
            "--coverage-threshold",
            "93",
        ],
    ):
        hatch.main()

    assert captured == {
        "project_name": "wizard-proj",
        "base_path": str(tmp_path),
        "template": "web",
        "coverage_threshold": 93,
    }


def test_cli_rejects_invalid_coverage_threshold():
    with patch.object(
        sys, "argv", ["hatch.py", "badproj", "--coverage-threshold", "200"]
    ):
        with pytest.raises(SystemExit) as exc:
            hatch.main()
    assert exc.value.code == 2
