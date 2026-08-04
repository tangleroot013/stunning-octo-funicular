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


def _target_run(adapter, args: List[str], q: Queue):
    try:
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
