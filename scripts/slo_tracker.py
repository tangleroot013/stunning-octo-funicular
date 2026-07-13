#!/usr/bin/env python3
"""Track SLO budget burn: error rate and latency from test run history."""

import json
from pathlib import Path

SLO = {
    "error_rate": 0.001,  # 0.1%
    "p99_latency_ms": 500,
    "availability": 0.999,  # 99.9%
}

HISTORY = Path(".slo_history.json")

def track() -> None:
    # Load current metrics
    current = {
        "error_rate": 0.0,
        "p99_latency_ms": float(Path(".last_runtime").read_text().strip()) if Path(".last_runtime").exists() else 0,
        "availability": 1.0 if Path(".last_test_ok").exists() else 0.0,
    }
    
    # Load history
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    hist.append({
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        **current,
    })
    hist = hist[-100:]  # rolling window
    HISTORY.write_text(json.dumps(hist, indent=2))
    
    # Calculate burn rates
    avg_error = sum(h.get("error_rate", 0) for h in hist) / len(hist)
    avg_latency = sum(h.get("p99_latency_ms", 0) for h in hist) / len(hist)
    uptime = sum(h.get("availability", 1) for h in hist) / len(hist)
    
    print(f"# SLO Budget Burn\n")
    print(f"{'Metric':<20} {'Current':<12} {'SLO':<12} {'Budget Left':<12}")
    print("-" * 60)
    
    for metric, target in SLO.items():
        current_val = current.get(metric, 0)
        if metric == "availability":
            budget = (target - (1 - uptime)) / target * 100
            status = "✅" if uptime >= target else "🔥"
            print(f"{status} {metric:<18} {uptime:.4f}      {target:.4f}      {budget:.1f}%")
        else:
            budget = (target - current_val) / target * 100 if target > 0 else 100
            status = "✅" if current_val <= target else "🔥"
            print(f"{status} {metric:<18} {current_val:.4f}      {target:.4f}      {budget:.1f}%")
    
    # Alert if burning too fast
    if avg_error > SLO["error_rate"] * 2:
        print(f"\n🚨 Error rate burning {avg_error/SLO['error_rate']:.1f}x SLO budget!")

if __name__ == "__main__":
    track()
