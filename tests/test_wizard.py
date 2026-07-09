"""Regression tests for the interactive scaffolding wizard."""

import sys
from unittest.mock import patch

import pytest

import hatch
import src.utils.wizard as wizard
from src.utils.wizard import (
    _is_valid_coverage,
    _is_valid_project_name,
    ask,
    choose,
    collect_answers,
    yes_no,
)


def test_project_name_validator():
    assert _is_valid_project_name("foo") is True
    assert _is_valid_project_name("foo-bar_v1") is True
    assert _is_valid_project_name("123") is False
    assert _is_valid_project_name("") is False
    assert _is_valid_project_name("foo bar") is False


def test_coverage_validator():
    assert _is_valid_coverage("85") is True
    assert _is_valid_coverage("0") is True
    assert _is_valid_coverage("100") is True
    assert _is_valid_coverage("101") is False
    assert _is_valid_coverage("abc") is False


def test_ask_uses_default_on_empty_input(monkeypatch):
    inputs = [""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    result = ask("Name", default="myproject")
    assert result == "myproject"


def test_ask_rejects_invalid_and_retries(monkeypatch):
    inputs = ["123", "valid"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    result = ask("Name", validator=_is_valid_project_name)
    assert result == "valid"


def test_choose_by_number(monkeypatch):
    inputs = ["2"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    result = choose(
        "Pick a template",
        [("cli", "CLI"), ("web", "Web"), ("lib", "Lib")],
        default="cli",
    )
    assert result == "web"


def test_choose_uses_default_on_empty_input(monkeypatch):
    inputs = [""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    result = choose(
        "Pick a template",
        [("cli", "CLI"), ("web", "Web"), ("lib", "Lib")],
        default="cli",
    )
    assert result == "cli"


def test_choose_rejects_invalid_input(monkeypatch):
    inputs = ["99", "1"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    result = choose(
        "Pick a template",
        [("cli", "CLI"), ("web", "Web"), ("lib", "Lib")],
        default="cli",
    )
    assert result == "cli"


def test_yes_no_defaults(monkeypatch):
    inputs = [""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    assert yes_no("Install global", default=False) is False

    inputs = [""]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    assert yes_no("Install global", default=True) is True


def test_collect_answers(monkeypatch, tmp_path):
    inputs = [
        "demo-project",
        "",  # template default
        str(tmp_path),  # base path
        "",  # coverage default
        "n",  # global templates
    ]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    answers = collect_answers()
    assert answers["project_name"] == "demo-project"
    assert answers["template"] == "cli"
    assert answers["base_path"] == str(tmp_path)
    assert answers["coverage_threshold"] == 85
    assert answers["setup_global"] is False


def test_hatch_main_runs_wizard_when_no_args(monkeypatch, tmp_path):
    seen_defaults = None

    def fake_collect(defaults=None):
        nonlocal seen_defaults
        seen_defaults = defaults
        return {
            "project_name": "wizard-test",
            "template": "cli",
            "base_path": str(tmp_path),
            "coverage_threshold": 90,
            "setup_global": False,
        }

    monkeypatch.setattr(hatch, "scaffold", lambda *args, **kwargs: tmp_path / args[0])
    monkeypatch.setattr(hatch, "collect_answers", fake_collect)

    with patch.object(sys, "argv", ["hatch.py"]):
        hatch.main()

    assert seen_defaults == {
        "template": "cli",
        "base_path": ".",
        "coverage_threshold": 85,
        "setup_global": False,
    }


def test_hatch_main_forwards_cli_flags_to_wizard(monkeypatch, tmp_path):
    seen_defaults = None

    def fake_collect(defaults=None):
        nonlocal seen_defaults
        seen_defaults = defaults
        return {
            "project_name": "wizard-test",
            "template": "web",
            "base_path": str(tmp_path),
            "coverage_threshold": 95,
            "setup_global": True,
        }

    monkeypatch.setattr(hatch, "scaffold", lambda *args, **kwargs: tmp_path / args[0])
    monkeypatch.setattr(hatch, "collect_answers", fake_collect)

    with patch.object(
        sys,
        "argv",
        ["hatch.py", "-t", "web", "-p", str(tmp_path), "--coverage-threshold", "95"],
    ):
        hatch.main()

    assert seen_defaults == {
        "template": "web",
        "base_path": str(tmp_path),
        "coverage_threshold": 95,
        "setup_global": False,
    }


def test_cli_coverage_threshold_is_used_in_scaffold(tmp_path, monkeypatch):
    project_dir = tmp_path / "cli-cov-test"
    monkeypatch.setattr(hatch, "init_git_repo", lambda p: None)
    monkeypatch.setattr(hatch, "create_git_hook", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "create_git_message", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "collect_answers", lambda defaults: {
        "project_name": "cli-cov-test",
        "template": "cli",
        "base_path": str(tmp_path),
        "coverage_threshold": 95,
        "setup_global": False,
    })
    monkeypatch.setattr(sys, "argv", ["hatch.py", "--coverage-threshold", "95"])
    hatch.main()
    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text()
    assert "pytest --cov . --cov-fail-under=95" in workflow


def test_cli_rejects_out_of_range_coverage_threshold(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["hatch.py", "--coverage-threshold", "200"])
    with pytest.raises(SystemExit) as exc:
        hatch.main()
    assert exc.value.code == 2


def test_scaffold_uses_coverage_threshold_in_workflow(tmp_path, monkeypatch):
    project_dir = tmp_path / "cov-test"
    monkeypatch.setattr(hatch, "init_git_repo", lambda p: None)
    monkeypatch.setattr(hatch, "create_git_hook", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "create_git_message", lambda p, **kw: None)
    hatch.scaffold("cov-test", str(tmp_path), "cli", coverage_threshold=90)
    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text()
    assert "pytest --cov . --cov-fail-under=90" in workflow


def test_scaffold_defaults_to_85_coverage_threshold(tmp_path, monkeypatch):
    project_dir = tmp_path / "cov-default"
    monkeypatch.setattr(hatch, "init_git_repo", lambda p: None)
    monkeypatch.setattr(hatch, "create_git_hook", lambda p, **kw: None)
    monkeypatch.setattr(hatch, "create_git_message", lambda p, **kw: None)
    hatch.scaffold("cov-default", str(tmp_path), "cli")
    workflow = (project_dir / ".github" / "workflows" / "pipeline.yml").read_text()
    assert "pytest --cov . --cov-fail-under=85" in workflow
