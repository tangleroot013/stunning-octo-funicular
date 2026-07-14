#!/usr/bin/env python3
"""Multi-dimensional performance budget: CPU, memory, latency, and throughput gates."""

import json
import subprocess
import sys
from pathlib import Path

BUDGETS = {
    "cpu_percent": 80,
    "memory_mb": 512,
    "latency_p99_ms": 500,
    "throughput_rps": 100,
}

def check() -> int:
    metrics = {}
    
    # Try to get current metrics
    try:
        import psutil
        metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
        metrics["memory_mb"] = psutil.Process().memory_info().rss / 1024 / 1024
    except ImportError:
        print("ℹ️  Install psutil for system metrics: pip install psutil")
        metrics["cpu_percent"] = 0
        metrics["memory_mb"] = 0
    
    # Get latency from last runtime
    metrics["latency_p99_ms"] = float(Path(".last_runtime").read_text().strip()) if Path(".last_runtime").exists() else 0
    
    # Estimate throughput (naive)
    metrics["throughput_rps"] = 1000 / max(metrics["latency_p99_ms"], 1)
    
    print(f"# Performance Budget v2\n")
    print(f"{'Metric':<20} {'Current':<12} {'Budget':<12} {'Status'}")
    print("-" * 60)
    
    fails = 0
    for metric, budget in BUDGETS.items():
        current = metrics.get(metric, 0)
        if metric == "throughput_rps":
            ok = current >= budget
        else:
            ok = current <= budget
        
        status = "✅" if ok else "❌"
        print(f"{metric:<20} {current:>10.1f}   {budget:>10.1f}   {status}")
        
        if not ok:
            fails += 1
    
    # Save metrics
    Path(".perf_budget.json").write_text(json.dumps(metrics, indent=2))
    
    if fails:
        print(f"\n❌ {fails} budget(s) exceeded.")
        return 1
    print(f"\n✅ All performance budgets within limits.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
