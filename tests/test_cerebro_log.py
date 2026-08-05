"""Tests for src/cerebro_log.py -- shell + pipeline unified logging."""
from __future__ import annotations

import sys

import pytest

from src import cerebro_log


@pytest.fixture(autouse=True)
def _isolate_log(tmp_path, monkeypatch):
    """Redirect LOG_PATH to a throwaway file for every test."""
    fake_log = tmp_path / "shell.log"
    monkeypatch.setattr(cerebro_log, "LOG_PATH", fake_log)
    return fake_log


def test_redact_hides_known_secret_markers():
    assert cerebro_log._redact("export API_KEY=xyz") == "[redacted]"
    assert cerebro_log._redact("normal command") == "normal command"


def test_log_event_writes_expected_format(_isolate_log):
    ok = cerebro_log.log_event("test_stage", 0, "extra info")
    assert ok is True
    content = _isolate_log.read_text()
    assert "exit=0" in content
    assert "cmd=ship:test_stage extra info" in content


def test_log_event_redacts_secrets_in_extra(_isolate_log):
    cerebro_log.log_event("deploy", 0, "TOKEN=abc123")
    content = _isolate_log.read_text()
    assert "TOKEN" not in content
    assert "[redacted]" in content


def test_log_event_returns_false_on_write_failure(tmp_path, monkeypatch):
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file, not a directory")
    bad_log_path = blocker / "shell.log"  # parent "blocker" is a file -> mkdir fails
    monkeypatch.setattr(cerebro_log, "LOG_PATH", bad_log_path)
    ok = cerebro_log.log_event("fail_stage", 1)
    assert ok is False


def test_rotate_if_needed_truncates_large_log(_isolate_log, monkeypatch):
    monkeypatch.setattr(cerebro_log, "MAX_BYTES", 50)
    monkeypatch.setattr(cerebro_log, "KEEP_LINES", 2)
    _isolate_log.write_text("\n".join(f"line{i}" for i in range(20)) + "\n")
    cerebro_log._rotate_if_needed()
    remaining = _isolate_log.read_text().splitlines()
    assert remaining == ["line18", "line19"]


def test_rotate_if_needed_noop_when_under_threshold(_isolate_log):
    _isolate_log.write_text("short\n")
    cerebro_log._rotate_if_needed()
    assert _isolate_log.read_text() == "short\n"


def test_main_cli_success(monkeypatch, capsys, _isolate_log):
    monkeypatch.setattr(sys, "argv", ["cerebro_log.py", "cli_stage", "0", "ran via cli"])
    ok = cerebro_log.main()
    assert ok is True
    out = capsys.readouterr().out
    assert "[ok] logged" in out


def test_main_cli_reports_failure(monkeypatch, capsys, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file, not a directory")
    monkeypatch.setattr(cerebro_log, "LOG_PATH", blocker / "shell.log")
    monkeypatch.setattr(sys, "argv", ["cerebro_log.py", "cli_stage", "1"])
    ok = cerebro_log.main()
    assert ok is False
    out = capsys.readouterr().out
    assert "[error] log failed" in out
