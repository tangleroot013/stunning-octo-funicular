#!/usr/bin/env python3
"""Label stale issues (no activity > 30 days) using gh CLI."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def label() -> int:
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", "tangleroot013/stunning-octo-funicular",
         "--json", "number,updatedAt,labels", "--state", "open", "-L", "100"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ gh CLI error: {result.stderr}")
        return 1
    
    issues = json.loads(result.stdout)
    now = datetime.now(timezone.utc)
    stale_label = "stale"
    
    labeled = 0
    for issue in issues:
        updated = datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
        days = (now - updated).days
        labels = [l["name"] for l in issue["labels"]]
        
        if days > 30 and stale_label not in labels:
            subprocess.run([
                "gh", "issue", "edit", str(issue["number"]),
                "--add-label", stale_label
            ], capture_output=True)
            print(f"🏷️  Issue #{issue['number']} labeled stale ({days} days inactive)")
            labeled += 1
    
    print(f"✅ Labeled {labeled} stale issue(s).")
    return 0

if __name__ == "__main__":
    sys.exit(label())
