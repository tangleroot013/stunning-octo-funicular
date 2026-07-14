#!/usr/bin/env python3
"""Track health score decay rate and predict when it will breach thresholds."""

import json
from datetime import datetime
from pathlib import Path

HISTORY = Path(".health_history.json")

def decay() -> None:
    if not HISTORY.exists():
        print("ℹ️  No health history. Run: python scripts/health_trend.py")
        return
    
    hist = json.loads(HISTORY.read_text())
    if len(hist) < 5:
        print("ℹ️  Need at least 5 data points.")
        return
    
    # Calculate decay rate (points per day)
    first = datetime.fromisoformat(hist[0]["ts"])
    last = datetime.fromisoformat(hist[-1]["ts"])
    days = (last - first).total_seconds() / 86400
    score_delta = hist[-1]["score"] - hist[0]["score"]
    
    if days == 0:
        print("ℹ️  All readings same day.")
        return
    
    decay_rate = score_delta / days  # negative = decaying
    
    print(f"# Health Decay Analysis\n")
    print(f"Period:     {days:.1f} days")
    print(f"Score:      {hist[0]['score']} → {hist[-1]['score']} (Δ{score_delta:+.1f})")
    print(f"Decay rate: {decay_rate:.2f} points/day")
    
    if decay_rate < 0:
        days_to_80 = (hist[-1]["score"] - 80) / abs(decay_rate) if hist[-1]["score"] > 80 else 0
        days_to_60 = (hist[-1]["score"] - 60) / abs(decay_rate) if hist[-1]["score"] > 60 else 0
        
        if days_to_80 > 0:
            print(f"\n🔮 Projected to drop below 80 in {days_to_80:.1f} days")
        if days_to_60 > 0:
            print(f"🔮 Projected to drop below 60 in {days_to_60:.1f} days")
        print(f"\n🚨 Health is decaying. Run: python scripts/auto_heal.py")
    else:
        print(f"\n✅ Health is improving or stable.")

if __name__ == "__main__":
    decay()
