#!/usr/bin/env python3
"""Send desktop notification if health score drops below threshold."""

import json
import subprocess
import sys
from pathlib import Path

THRESHOLD = 70

def alert() -> int:
    score_file = Path(".health_score")
    if not score_file.exists():
        print("ℹ️  No health score. Run: python scripts/health_score.py")
        return 0
    
    score = int(score_file.read_text().strip())
    if score >= THRESHOLD:
        print(f"✅ Health score {score} ≥ {THRESHOLD}")
        return 0
    
    msg = f"🚨 Health score dropped to {score} (threshold: {THRESHOLD})"
    print(msg)
    
    for notifier in ("notify-send", "osascript", "zenity"):
        if subprocess.run(["which", notifier], capture_output=True).returncode == 0:
            if notifier == "notify-send":
                subprocess.run(["notify-send", "stunning-octo-funicular", msg])
            elif notifier == "osascript":
                subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "Health Alert"'])
            break
    
    # Also write to alert log
    hist = Path(".health_alerts")
    hist.write_text(hist.read_text() + f"\\n{__import__('datetime').datetime.now().isoformat()} {msg}" if hist.exists() else f"{__import__('datetime').datetime.now().isoformat()} {msg}")
    return 1

if __name__ == "__main__":
    sys.exit(alert())
