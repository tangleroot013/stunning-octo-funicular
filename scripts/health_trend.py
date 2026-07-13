#!/usr/bin/env python3
"""Track health score over time and plot ASCII trend from .health_score history."""

import json
from datetime import datetime
from pathlib import Path

HISTORY = Path(".health_history.json")

def record() -> None:
    score_file = Path(".health_score")
    if not score_file.exists():
        print("ℹ️  No .health_score found. Run: python scripts/health_score.py")
        return
    
    score = int(score_file.read_text().strip())
    entry = {"ts": datetime.now().isoformat(), "score": score}
    
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    hist.append(entry)
    hist = hist[-30:]  # rolling 30
    HISTORY.write_text(json.dumps(hist, indent=2))
    
    # ASCII sparkline
    scores = [h["score"] for h in hist]
    blocks = "▁▂▃▄▅▆▇█"
    mn, mx = min(scores), max(scores)
    if mx == mn:
        spark = "█" * len(scores)
    else:
        spark = "".join(blocks[int((s - mn) / (mx - mn) * 7)] for s in scores)
    
    print(f"Health Trend (last {len(scores)} runs)")
    print(f"  {spark}")
    print(f"  {mn} ← range → {mx}  (latest: {score})")

if __name__ == "__main__":
    record()
