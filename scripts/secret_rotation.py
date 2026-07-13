#!/usr/bin/env python3
"""Detect secrets older than 90 days and flag for rotation."""

import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"(API_KEY|SECRET|TOKEN|PWD|PASSWORD)\\s*=\\s*['\"]([^'\"]{8,})['\"]"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"sk-[a-zA-Z0-9]{48}"),
]

def audit() -> int:
    hits = 0
    cutoff = datetime.now() - timedelta(days=90)
    
    for py in Path("src").rglob("*.py"):
        blame = subprocess.run(
            ["git", "blame", "--date=short", "-l", str(py)],
            capture_output=True, text=True, errors="ignore"
        )
        
        for line in blame.stdout.splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            date_str = parts[1]
            try:
                line_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            
            if line_date < cutoff:
                content = " ".join(parts[2:])
                for pat in SECRET_PATTERNS:
                    if pat.search(content):
                        print(f"🚨 {py}: secret from {date_str} (>90 days old)")
                        print(f"   Rotate: {content[:60]}...")
                        hits += 1
                        break
    
    if hits:
        print(f"\n❌ {hits} secret(s) older than 90 days. Rotate immediately.")
        return 1
    print("✅ All secrets within rotation window.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
