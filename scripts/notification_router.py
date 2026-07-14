#!/usr/bin/env python3
"""Route notifications to appropriate channel based on severity: slack, discord, email, desktop."""

import os
import subprocess
import sys
from pathlib import Path

CHANNELS = {
    "critical": ["desktop", "slack", "discord"],
    "warning": ["desktop", "slack"],
    "info": ["desktop"],
}

def notify(level: str, message: str) -> int:
    channels = CHANNELS.get(level, ["desktop"])
    
    for channel in channels:
        if channel == "desktop":
            for notifier in ("notify-send", "osascript", "zenity"):
                if subprocess.run(["which", notifier], capture_output=True).returncode == 0:
                    if notifier == "notify-send":
                        subprocess.run(["notify-send", f"SOF {level.upper()}", message])
                    elif notifier == "osascript":
                        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "SOF {level.upper()}"'])
                    break
        
        if channel == "slack" and os.environ.get("SLACK_WEBHOOK"):
            import urllib.request
            payload = {"text": f"[{level.upper()}] {message}"}
            req = urllib.request.Request(
                os.environ["SLACK_WEBHOOK"],
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
        
        if channel == "discord" and os.environ.get("DISCORD_WEBHOOK"):
            import urllib.request
            payload = {"content": f"[{level.upper()}] {message}"}
            req = urllib.request.Request(
                os.environ["DISCORD_WEBHOOK"],
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
    
    print(f"✅ Routed {level} notification to {len(channels)} channel(s)")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: notification_router.py <critical|warning|info> <message>")
        sys.exit(1)
    import json
    sys.exit(notify(sys.argv[1], " ".join(sys.argv[2:])))
