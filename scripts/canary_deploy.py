#!/usr/bin/env python3
"""Canary deployment simulator: deploy to subset, monitor, then full rollout or rollback."""

import random
import subprocess
import time
from pathlib import Path

CANARY_SIZE = 10  # percent

def deploy() -> int:
    print(f"🐤 Canary deployment: {CANARY_SIZE}% traffic\n")
    
    # 1. Build
    print("1. Building...")
    build = subprocess.run(["python", "scripts/docker_build.py"], capture_output=True)
    if build.returncode != 0:
        print("❌ Build failed. Abort.")
        return 1
    
    # 2. Deploy canary
    print(f"2. Deploying canary ({CANARY_SIZE}%)...")
    # Simulate canary health check
    canary_healthy = random.random() > 0.1  # 90% success rate for demo
    
    if not canary_healthy:
        print("❌ Canary unhealthy. Rolling back...")
        subprocess.run(["python", "scripts/notification_router.py", "critical", "Canary failed, rolled back"], capture_output=True)
        return 1
    
    # 3. Monitor window
    print("3. Monitoring canary (30s)...")
    time.sleep(3)  # shortened for demo
    
    # 4. Full rollout
    print("4. Canary healthy. Full rollout...")
    print("✅ Deployment complete.")
    subprocess.run(["python", "scripts/notification_router.py", "info", "Canary deployment successful"], capture_output=True)
    return 0

if __name__ == "__main__":
    sys.exit(deploy())
