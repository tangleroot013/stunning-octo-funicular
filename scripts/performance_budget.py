#!/usr/bin/env python3
"""Fail if .last_runtime exceeds the budget in settings.json."""

import json
from pathlib import Path

def check() -> int:
    data = json.loads(Path("settings.json").read_text())
    budget_ms = data.get("testing", {}).get("performance_budget_ms", 5000)
    runtime = float(Path(".last_runtime").read_text().strip())
    if runtime > budget_ms:
        print(f"❌ Runtime {runtime}ms exceeds budget {budget_ms}ms")
        return 1
    print(f"✅ Runtime {runtime}ms within budget {budget_ms}ms")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(check())
