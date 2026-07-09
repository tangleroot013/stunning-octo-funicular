"""Regression tests for env_checker.py."""

import sys
from unittest.mock import patch

import pytest

import hatch
from src.utils import env_checker
from src.utils.env_checker import (
    ToolStatus,
    _venv_module_available,
    check_environment,
    format_report,
)


def test_venv_module_available():
    """venv is part of the standard library in modern CPython."""
    assert _venv_module_available() is True


def test_check_environment_passes_when_all_present(monkeypatch):
    """All required tools are present in this environment; optional tools are reported."""
    monkeypatch.setattr(env_checker, "_python_meets_minimum", lambda: True)
    monkeypatch.setattr(env_checker, "_venv_module_available", lambda: True)
    monkeypatch.setattr(
        env_checker,
        "_load_tool_lists",
        lambda: (
            {"python3": "Python", "pip3": "pip", "git": "Git"},
            {"ruff": "Ruff"},
        ),
    )
    monkeypatch.setattr(
        env_checker.shutil,
        "which",
        lambda tool: f"/usr/bin/{tool}" if tool in {"python3", "pip3", "git", "ruff"} else None,
    )
    monkeypatch.setattr(
        env_checker.subprocess,
        "run",
        lambda *args, **kwargs: type(
            "Result",
            (),
            {"returncode": 0, "stdout": f"{args[0][0]} 1.0\n", "stderr": ""},
        )(),
    )

    passed, statuses = check_environment(include_optional=True)
    assert passed is True
    assert all(s.available for s in statuses if s.name in {"python3", "venv", "pip3", "git", "ruff"})


def test_check_environment_fails_when_tool_missing(monkeypatch):
    monkeypatch.setattr(env_checker, "_python_meets_minimum", lambda: True)
    monkeypatch.setattr(env_checker, "_venv_module_available", lambda: True)
    monkeypatch.setattr(
        env_checker,
        "_load_tool_lists",
        lambda: ({"python3": "Python", "git": "Git"}, {}),
    )
    monkeypatch.setattr(env_checker.shutil, "which", lambda tool: None)

    passed, statuses = check_environment(include_optional=False)
    assert passed is False
    assert all(not s.available for s in statuses if s.name in {"git"})


def test_check_environment_respects_include_optional_flag(monkeypatch):
    monkeypatch.setattr(env_checker, "_python_meets_minimum", lambda: True)
    monkeypatch.setattr(env_checker, "_venv_module_available", lambda: True)
    monkeypatch.setattr(
        env_checker,
        "_load_tool_lists",
        lambda: ({"git": "Git"}, {"ruff": "Ruff"}),
    )
    monkeypatch.setattr(env_checker.shutil, "which", lambda tool: "/usr/bin/{tool}")

    passed_required, statuses_required = check_environment(include_optional=False)
    passed_all, statuses_all = check_environment(include_optional=True)
    assert passed_required is True
    assert passed_all is True
    assert len(statuses_all) > len(statuses_required)
    assert any(s.name == "ruff" for s in statuses_all)
    assert not any(s.name == "ruff" for s in statuses_required)


def test_check_environment_fails_on_old_python(monkeypatch):
    monkeypatch.setattr(env_checker, "_python_meets_minimum", lambda: False)
    monkeypatch.setattr(env_checker, "_venv_module_available", lambda: True)
    monkeypatch.setattr(env_checker, "_load_tool_lists", lambda: ({}, {}))

    passed, statuses = check_environment(include_optional=False)
    assert passed is False
    python_status = next(s for s in statuses if s.name == "python3")
    assert python_status.available is False
    assert "Python 3.7+ is required" in python_status.message


def test_format_report_shows_all_statuses():
    statuses = [
        ToolStatus(name="python3", label="Python", available=True, version="3.10"),
        ToolStatus(name="git", label="Git", available=False, message="git missing"),
    ]
    report = format_report(statuses, False)
    assert "Environment Pre-flight Check" in report
    assert "Python" in report
    assert "Git" in report
    assert "git missing" in report
    assert "Some requirements are missing" in report


def test_hatch_cli_check_env(monkeypatch):
    def fake_check(include_optional=True):
        return True, [
            ToolStatus(name="python3", label="Python", available=True, version="3.10")
        ]

    monkeypatch.setattr(hatch, "check_environment", fake_check)
    monkeypatch.setattr(hatch, "format_report", lambda statuses, passed: "OK")

    with pytest.raises(SystemExit) as exc:
        with patch.object(sys, "argv", ["hatch.py", "--check-env"]):
            hatch.main()
    assert exc.value.code == 0


def test_hatch_cli_check_env_fails_when_check_fails(monkeypatch):
    def fake_check(include_optional=True):
        return False, [
            ToolStatus(name="git", label="Git", available=False, message="missing")
        ]

    monkeypatch.setattr(hatch, "check_environment", fake_check)
    monkeypatch.setattr(hatch, "format_report", lambda statuses, passed: "FAIL")

    with pytest.raises(SystemExit) as exc:
        with patch.object(sys, "argv", ["hatch.py", "--check-env"]):
            hatch.main()
    assert exc.value.code == 1
