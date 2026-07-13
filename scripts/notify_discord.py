#!/usr/bin/env python3
"""Send health score and build status to Discord webhook (reads from env)."""

import json
import os
import sys
import urllib.request
from pathlib import Path

def notify() -> int:
    webhook = os.environ.get("DISCORD_WEBHOOK")
    if not webhook:
        print("ℹ️  Set DISCORD_WEBHOOK env var to enable notifications.")
        return 0
    
    score = Path(".health_score").read_text().strip() if Path(".health_score").exists() else "?"
    status = "🟢" if score != "?" and int(score) >= 80 else "🟡" if score != "?" and int(score) >= 60 else "🔴"
    
    payload = {
        "content": f"{status} **stunning-octo-funicular** health: {score}/100",
        "embeds": [{
            "title": "Build Status",
            "fields": [
                {"name": "Coverage", "value": Path(".last_cov_score").read_text().strip() + "%", "inline": True},
                {"name": "Tests", "value": "✅" if Path(".last_test_ok").exists() else "❌", "inline": True},
            ]
        }]
    }
    
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req, timeout=5)
    print("✅ Discord notification sent.")
    return 0

if __name__ == "__main__":
    sys.exit(notify())
