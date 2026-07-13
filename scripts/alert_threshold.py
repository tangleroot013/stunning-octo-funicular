#!/usr/bin/env python3
"""Alert if coverage drops below the threshold in settings.json."""

import json
import sys
from pathlib import Path

def check() -> int:
    data = json.loads(Path("settings.json").read_text())
    threshold = data["testing"]["coverage"]["threshold"]
    current = float(Path(".last_cov_score").read_text().strip())
    if current < threshold:
        print(f"🚨 Coverage {current}% below threshold {threshold}%")
        return 1
    print(f"✅ Coverage {current}% meets threshold {threshold}%")
    return 0

if __name__ == "__main__":
    sys.exit(check())
