#!/usr/bin/env python3
"""Stress-test the local FastAPI server and report latency percentiles."""

import json
import sys
import threading
import time
from urllib.request import urlopen
from pathlib import Path

def stress(url: str, threads: int = 10, requests: int = 100) -> int:
    latencies = []
    lock = threading.Lock()
    
    def worker():
        for _ in range(requests // threads):
            t0 = time.perf_counter()
            try:
                urlopen(url, timeout=5)
            except Exception:
                pass
            with lock:
                latencies.append((time.perf_counter() - t0) * 1000)
    
    print(f"🔥 Stressing {url} with {threads} threads × {requests // threads} requests...")
    t0 = time.perf_counter()
    pool = [threading.Thread(target=worker) for _ in range(threads)]
    for t in pool: t.start()
    for t in pool: t.join()
    total = (time.perf_counter() - t0) * 1000
    
    if not latencies:
        print("❌ No successful requests.")
        return 1
    
    latencies.sort()
    p50 = latencies[len(latencies)//2]
    p99 = latencies[int(len(latencies)*0.99)]
    print(f"✅ {len(latencies)} requests in {total:.0f}ms")
    print(f"   p50: {p50:.1f}ms | p99: {p99:.1f}ms | avg: {sum(latencies)/len(latencies):.1f}ms")
    return 0

if __name__ == "__main__":
    cfg = json.loads(Path("settings.json").read_text())["web"]["server"]
    url = f"http://{cfg['host']}:{cfg['port']}/health"
    sys.exit(stress(url))
