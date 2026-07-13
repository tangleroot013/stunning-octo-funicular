#!/usr/bin/env python3
"""Desktop notification when a long command finishes. Usage: notify_done.py <cmd> [args...]"""

import subprocess
import sys
from pathlib import Path

def notify(msg: str) -> None:
    for notifier in ("notify-send", "osascript", "zenity"):
        if subprocess.run(["which", notifier], capture_output=True).returncode == 0:
            if notifier == "notify-send":
                subprocess.run(["notify-send", "Done", msg])
            elif notifier == "osascript":
                subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "Done"'])
            break

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: notify_done.py <command> [args...]")
        return 1
    result = subprocess.run(sys.argv[1:])
    status = "success" if result.returncode == 0 else "failure"
    notify(f"{'✅' if result.returncode == 0 else '❌'} {' '.join(sys.argv[1:])} → {status}")
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
