#!/usr/bin/env python3
"""Wrap any command with a timeout and graceful SIGTERM → SIGTERM escalation."""

import signal
import subprocess
import sys
import time

def wrap(cmd: list[str], seconds: int = 60) -> int:
    proc = subprocess.Popen(cmd)
    try:
        return proc.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout after {seconds}s — sending SIGTERM...")
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("💥 SIGKILL")
            proc.kill()
        return 124

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: timeout_wrap.py <seconds> <command...>")
        sys.exit(1)
    sys.exit(wrap(sys.argv[2:], int(sys.argv[1])))
