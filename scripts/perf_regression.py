#!/usr/bin/env python3
"""Compare current test runtime against historical average and flag regressions."""

import json
from pathlib import Path

HISTORY = Path(".runtime_history.json")
THRESHOLD_PCT = 20  # flag if >20% slower than average

def check() -> int:
    current = float(Path(".last_runtime").read_text().strip()) if Path(".last_runtime").exists() else 0
    if not HISTORY.exists():
        print("ℹ️  No runtime history. Creating baseline.")
        HISTORY.write_text(json.dumps([{"runtime": current}], indent=2))
        return 0
    
    hist = json.loads(HISTORY.read_text())
    avg = sum(h["runtime"] for h in hist) / len(hist)
    pct = (current - avg) / avg * 100 if avg else 0
    
    print(f"Runtime: {current:.0f}ms | Average: {avg:.0f}ms | Δ{pct:+.1f}%")
    
    hist.append({"runtime": current})
    HISTORY.write_text(json.dumps(hist[-20:], indent=2))
    
    if pct > THRESHOLD_PCT:
        print(f"❌ Regression detected: {pct:.1f}% slower than average.")
        return 1
    print("✅ Runtime within normal range.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(check())
