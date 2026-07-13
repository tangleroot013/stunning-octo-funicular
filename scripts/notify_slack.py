#!/usr/bin/env python3
"""Send build status to Slack webhook (reads SLACK_WEBHOOK from env)."""

import json
import os
import urllib.request
from pathlib import Path

def notify() -> int:
    webhook = os.environ.get("SLACK_WEBHOOK")
    if not webhook:
        print("ℹ️  Set SLACK_WEBHOOK env var to enable Slack notifications.")
        return 0
    
    score = Path(".health_score").read_text().strip() if Path(".health_score").exists() else "?"
    status = "success" if score != "?" and int(score) >= 80 else "failure" if score != "?" and int(score) < 60 else "warning"
    
    payload = {
        "text": f"stunning-octo-funicular build {status.upper()}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"Build {status.upper()}"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Health:*\\n{score}/100"},
                {"type": "mrkdwn", "text": f"*Coverage:*\\n{Path('.last_cov_score').read_text().strip() if Path('.last_cov_score').exists() else '?'}%"},
            ]}
        ]
    }
    
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req, timeout=5)
    print("✅ Slack notification sent.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(notify())
