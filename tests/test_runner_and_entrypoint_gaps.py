"""
Coverage-gap tests for src/plugins/runner.py, src/__main__.py, and the
write_file() dry-run branch in src/hatch.py.

NOTE ON runner.py: _target_run() monkeypatches subprocess.run, subprocess.Popen,
and os.system and NEVER restores them -- it relies on being called inside a
forked/spawned child process (multiprocessing) where that's harmless. Calling
it directly in-process (as these unit tests do) would otherwise leak the
patched functions into every later test in the session. The autouse fixture
below saves/restores all three around every test in this module so nothing
else in the suite gets silently poisoned. Worth fixing at the source too
(add a try/finally in _target_run) -- flagging it here rather than papering
over it.
"""
import os
import queue
import runpy
import subprocess
from unittest.mock import patch

import pytest

from src.plugins.runner import _command_is_allowed, _target_run


# ----------------------------------------------------------------------------
# Safety net: runner.py's _target_run patches subprocess.run/Popen/os.system
# and never restores them. Guard every test in this module against that leak.
# ----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _restore_global_subprocess_hooks():
    orig_run = subprocess.run
    orig_popen = subprocess.Popen
    orig_system = os.system
    yield
    subprocess.run = orig_run
    subprocess.Popen = orig_popen
    os.system = orig_system


# ----------------------------------------------------------------------------
# _command_is_allowed
# ----------------------------------------------------------------------------
class _BadStr:
    """Raises on str() to exercise the join-failure fallback branch."""
    def __str__(self):
        raise ValueError("boom")


def test_command_is_allowed_list_match():
    assert _command_is_allowed(["git", "push"], ["git"]) is True


def test_command_is_allowed_list_no_match():
    assert _command_is_allowed(["rm", "-rf"], ["git"]) is False


def test_command_is_allowed_str_cmd_match():
    assert _command_is_allowed("git push origin", ["git"]) is True


def test_command_is_allowed_empty_or_none_patterns():
    assert _command_is_allowed(["git"], None) is False
    assert _command_is_allowed(["git"], []) is False


def test_command_is_allowed_str_conversion_failure_falls_back():
    # str(x) raises inside the join -> except branch -> s = str(cmd)
    assert _command_is_allowed([_BadStr()], None) is False


# ----------------------------------------------------------------------------
# _target_run
# ----------------------------------------------------------------------------
class _OkAdapter:
    name = "ok_adapter"

    def run(self, args):
        return 0


class _FailAdapter:
    name = "fail_adapter"

    def run(self, args):
        raise ValueError("boom")


class _SubprocessAdapter:
    name = "sub_adapter"

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, args):
        return subprocess.run(self.cmd).returncode


class _PopenAdapter:
    name = "popen_adapter"

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, args):
        subprocess.Popen(self.cmd)
        return 0


class _SystemAdapter:
    name = "system_adapter"

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, args):
        os.system(self.cmd)
        return 0


@patch("src.plugins.config.get_policy")
def test_target_run_success_no_policy(mock_policy):
    mock_policy.return_value = {}
    q = queue.Queue()
    _target_run(_OkAdapter(), [], q)
    assert q.get() == (0, None)


@patch("src.plugins.config.get_policy")
def test_target_run_adapter_raises(mock_policy):
    mock_policy.return_value = {}
    q = queue.Queue()
    _target_run(_FailAdapter(), [], q)
    rc, err = q.get()
    assert rc == 1
    assert "boom" in err


@patch("src.plugins.config.get_policy")
def test_target_run_policy_lookup_raises_falls_back_to_none(mock_policy):
    mock_policy.side_effect = RuntimeError("no policy for you")
    q = queue.Queue()
    _target_run(_OkAdapter(), [], q)
    assert q.get() == (0, None)


@patch("src.plugins.config.get_policy")
def test_target_run_guarded_subprocess_run_allowed(mock_policy):
    mock_policy.return_value = {"allowed_commands": ["echo"]}
    q = queue.Queue()
    _target_run(_SubprocessAdapter(["echo", "hi"]), [], q)
    rc, err = q.get()
    assert rc == 0
    assert err is None


@patch("src.plugins.config.get_policy")
def test_target_run_guarded_subprocess_run_disallowed(mock_policy):
    mock_policy.return_value = {"allowed_commands": ["echo"]}
    q = queue.Queue()
    _target_run(_SubprocessAdapter(["rm", "-rf", "/"]), [], q)
    rc, err = q.get()
    assert rc == 1
    assert "disallowed subprocess command" in err


@patch("src.plugins.config.get_policy")
def test_target_run_guarded_popen_disallowed(mock_policy):
    mock_policy.return_value = {"allowed_commands": ["echo"]}
    q = queue.Queue()
    _target_run(_PopenAdapter(["rm", "-rf", "/"]), [], q)
    rc, err = q.get()
    assert rc == 1
    assert "disallowed subprocess command" in err


@patch("src.plugins.config.get_policy")
def test_target_run_guarded_os_system_disallowed(mock_policy):
    mock_policy.return_value = {"allowed_commands": ["echo"]}
    q = queue.Queue()
    _target_run(_SystemAdapter("rm -rf /"), [], q)
    rc, err = q.get()
    assert rc == 1
    assert "disallowed os.system command" in err


# ----------------------------------------------------------------------------
# src/__main__.py entrypoint (only covered when run as __main__, not on import)
# ----------------------------------------------------------------------------
def test_main_module_entrypoint_invokes_hatch_main():
    with patch("src.hatch.main", return_value=0) as mock_main:
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("src", run_name="__main__")
    assert exc_info.value.code == 0
    mock_main.assert_called_once()


# ----------------------------------------------------------------------------
# hatch.write_file dry-run branch
# ----------------------------------------------------------------------------
def test_write_file_dry_run_does_not_write(tmp_path, capsys):
    from src.hatch import write_file

    target = tmp_path / "sub" / "out.txt"
    write_file(target, "hello", dry_run=True)
    captured = capsys.readouterr()
    assert "[dry-run] would write" in captured.out
    assert not target.exists()


def test_write_file_writes_content(tmp_path):
    from src.hatch import write_file

    target = tmp_path / "sub" / "out.txt"
    write_file(target, "hello world")
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "hello world"

