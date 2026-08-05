#!/usr/bin/env python3
"""Unified logging for CerebroFlow: shell precmd hook + ship.py pipeline both
append to the same file, so shell.log becomes one timeline across interactive
commands and pipeline runs. Individually CLI-runnable and integrateable into
ship.py's STEPS list as a single callable returning bool."""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path.home() / ".local" / "state" / "cerebroflow" / "shell.log"
MAX_BYTES = 1_048_576  # 1MB, matches the zsh-side rotation threshold
KEEP_LINES = 2000
REDACT_MARKERS = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "api_key")


def _redact(text: str) -> str:
    return "[redacted]" if any(m in text for m in REDACT_MARKERS) else text


def _rotate_if_needed() -> None:
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_BYTES:
            lines = LOG_PATH.read_text().splitlines()[-KEEP_LINES:]
            LOG_PATH.write_text("\n".join(lines) + "\n")
    except OSError:
        pass  # logging must never break the pipeline


def log_event(stage: str, exit_code: int, extra: str = "") -> bool:
    """Append one line to the shared shell.log. Never raises; returns False
    on I/O failure so callers can decide whether that should fail a step."""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        cmd = _redact(f"ship:{stage} {extra}".strip())
        line = f"{ts}\texit={exit_code}\tpwd={os.getcwd()}\tcmd={cmd}\n"
        with LOG_PATH.open("a") as f:
            f.write(line)
        _rotate_if_needed()
        return True
    except OSError as e:
        print(f"[error] cerebro_log write failed: {e}", file=sys.stderr)
        return False


def main() -> bool:
    p = argparse.ArgumentParser(description="Log a pipeline stage/run to shell.log")
    p.add_argument("stage")
    p.add_argument("exit_code", type=int)
    p.add_argument("extra", nargs="?", default="")
    args = p.parse_args()
    ok = log_event(args.stage, args.exit_code, args.extra)
    print("[ok] logged" if ok else "[error] log failed")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
