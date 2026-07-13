#!/usr/bin/env python3
"""Forecast next health score using simple linear regression on historical data."""

import json
from pathlib import Path

HISTORY = Path(".health_history.json")

def forecast() -> None:
    if not HISTORY.exists() or HISTORY.stat().st_size < 100:
        print("ℹ️  Insufficient history. Run: python scripts/health_trend.py")
        return
    
    hist = json.loads(HISTORY.read_text())
    if len(hist) < 3:
        print("ℹ️  Need at least 3 data points.")
        return
    
    # Simple linear regression on last N points
    n = min(len(hist), 10)
    xs = list(range(n))
    ys = [h["score"] for h in hist[-n:]]
    
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / sum((x - x_mean) ** 2 for x in xs)
    intercept = y_mean - slope * x_mean
    
    next_score = slope * n + intercept
    trend = "improving" if slope > 0.5 else "declining" if slope < -0.5 else "stable"
    
    print(f"# Health Forecast\n")
    print(f"Trend:     {trend} (slope: {slope:+.2f}/run)")
    print(f"Next run:  {next_score:.0f}/100")
    print(f"Current:   {ys[-1]}/100")
    
    if next_score < 60:
        print(f"\n🔴 Projected to drop below 60. Intervene now.")
    elif next_score < 80:
        print(f"\n🟡 Projected to drop below 80. Monitor closely.")

if __name__ == "__main__":
    forecast()
