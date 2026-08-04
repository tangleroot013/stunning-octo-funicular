"""Run adapters under a controlled policy.

Provides run_adapter(adapter, args, timeout_seconds, allowed_args) which:
- Validates args against allowed_args (whitelist)
- Executes adapter.run(args) in a separate process using multiprocessing to
  enforce a timeout and to isolate potentially unsafe adapter behavior
- Returns (exit_code, timed_out_bool, error_message_or_none)
"""
from multiprocessing import Process, Queue
from typing import List, Tuple, Optional
import time


def _command_is_allowed(cmd, allowed_patterns):
    """Return True if the command (list or str) matches any allowed pattern."""
    s = cmd
    if isinstance(cmd, (list, tuple)):
        try:
            s = " ".join(str(x) for x in cmd)
        except Exception:
            s = str(cmd)
    for p in (allowed_patterns or []):
        # simple containment check for now
        if p and p in s:
            return True
    return False


def _target_run(adapter, args: List[str], q: Queue):
    try:
        # Load per-adapter policy for allowed_commands if available
        allowed_patterns = None
        try:
            from .config import get_policy
            allowed_patterns = get_policy(getattr(adapter, 'name', '')).get('allowed_commands')
        except Exception:
            allowed_patterns = None

        # Monkeypatch subprocess.run, subprocess.Popen and os.system to enforce allowed commands
        import subprocess as _sub
        import os as _os
        _orig_run = _sub.run
        _orig_popen = _sub.Popen
        _orig_system = _os.system

        def _guarded_run(cmd, *a, **kw):
            if allowed_patterns is not None and not _command_is_allowed(cmd, allowed_patterns):
                raise RuntimeError(f"disallowed subprocess command: {cmd}")
            return _orig_run(cmd, *a, **kw)

        class _GuardedPopen(_orig_popen):
            def __init__(self, cmd, *a, **kw):
                if allowed_patterns is not None and not _command_is_allowed(cmd, allowed_patterns):
                    raise RuntimeError(f"disallowed subprocess command: {cmd}")
                super().__init__(cmd, *a, **kw)

        def _guarded_system(cmd):
            if allowed_patterns is not None and not _command_is_allowed(cmd, allowed_patterns):
                raise RuntimeError(f"disallowed os.system command: {cmd}")
            return _orig_system(cmd)

        _sub.run = _guarded_run
        _sub.Popen = _GuardedPopen
        _os.system = _guarded_system

        rc = adapter.run(args)
        q.put((int(rc), None))
    except Exception as exc:
        q.put((1, str(exc)))


def run_adapter(adapter, args: List[str], timeout_seconds: int = 120, allowed_args: Optional[List[str]] = None) -> Tuple[int, bool, Optional[str]]:
    """Run adapter with policy enforcement.

    If allowed_args is None, consult the adapters.yaml policy for this adapter name.
    """
    # If no explicit allowed_args provided, try to load from config
    if allowed_args is None:
        try:
            from .config import get_policy
            policy = get_policy(getattr(adapter, 'name', ''))
            allowed_args = policy.get('allowed_args') if isinstance(policy.get('allowed_args'), list) else None
            if timeout_seconds == 120:
                # only override timeout if default not changed
                timeout_seconds = policy.get('timeout_seconds', timeout_seconds)
        except Exception:
            allowed_args = ['--exec']
    """Run adapter with policy enforcement.

    Returns a tuple: (exit_code, timed_out, error_message)
    - exit_code: adapter exit code (or 1 on error)
    - timed_out: True if execution was terminated due to timeout
    - error_message: None on success, str when adapter raised
    """
    # Basic argument validation: only allow flags explicitly listed
    allowed = set(allowed_args or ["--exec"])
    for a in args:
        # allow positional empty or permissive (none) - only validate flags
        if a.startswith("-") and a not in allowed:
            return 3, False, f"disallowed arg: {a}"

    q: Queue = Queue()
    p = Process(target=_target_run, args=(adapter, args, q), daemon=True)
    p.start()
    p.join(timeout_seconds)
    if p.is_alive():
        try:
            p.terminate()
        except Exception:
            pass
        return 124, True, "timed out"

    if not q.empty():
        rc, err = q.get()
        if err:
            return rc, False, err
        return rc, False, None
    # If no result, return error
    return 1, False, "no result from adapter"
