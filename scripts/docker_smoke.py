#!/usr/bin/env python3
"""Run container from built image and hit /health endpoint."""

import json
import subprocess
import sys
import time
from urllib.request import urlopen
from pathlib import Path

def smoke() -> int:
    data = json.loads(Path("settings.json").read_text())
    pkg = data["library"]["package_name"]
    port = data["web"]["server"]["port"]
    
    print(f"🐳 Starting {pkg}:latest on port {port}...")
    proc = subprocess.Popen(
        ["docker", "run", "--rm", "-d", "-p", f"{port}:{port}", "--name", "smoke_test", f"{pkg}:latest"],
        stdout=subprocess.PIPE, text=True
    )
    cid = proc.stdout.read().strip()
    time.sleep(3)
    
    try:
        resp = urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        print(f"✅ Container health check: {resp.status}")
        return 0
    except Exception as exc:
        print(f"❌ Health check failed: {exc}")
        return 1
    finally:
        subprocess.run(["docker", "stop", cid], capture_output=True)
        subprocess.run(["docker", "rm", cid], capture_output=True)

if __name__ == "__main__":
    sys.exit(smoke())
