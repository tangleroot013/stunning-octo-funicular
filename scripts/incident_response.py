#!/usr/bin/env python3
"""Automated incident response: detect failure, snapshot state, notify, and attempt recovery."""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def respond() -> int:
    print(f"🚨 Incident detected at {datetime.now().isoformat()}\n")
    
    # 1. Snapshot current state
    print("1. Creating incident snapshot...")
    subprocess.run(["python", "scripts/auto_snapshot.py"], capture_output=True)
    
    # 2. Collect diagnostics
    print("2. Collecting diagnostics...")
    diag = Path(f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "health": Path(".health_score").read_text().strip() if Path(".health_score").exists() else "unknown",
        "tests": "pass" if Path(".last_test_ok").exists() else "fail",
        "coverage": Path(".last_cov_score").read_text().strip() if Path(".last_cov_score").exists() else "unknown",
    }
    import json
    diag.write_text(json.dumps(diagnostics, indent=2))
    
    # 3. Notify
    print("3. Sending notifications...")
    subprocess.run(["python", "scripts/notification_router.py", "critical", f"SOF incident: health={diagnostics['health']}"], capture_output=True)
    
    # 4. Attempt auto-heal
    print("4. Attempting auto-heal...")
    heal_result = subprocess.run(["python", "scripts/auto_heal.py"], capture_output=True)
    
    # 5. Verify
    print("5. Verifying recovery...")
    health = subprocess.run(["python", "scripts/health_score.py"], capture_output=True)
    
    if health.returncode == 0:
        print("\n✅ Incident resolved automatically.")
        subprocess.run(["python", "scripts/notification_router.py", "info", "SOF incident resolved"], capture_output=True)
        return 0
    
    print("\n❌ Auto-recovery failed. Manual intervention required.")
    print(f"   Diagnostics: {diag}")
    subprocess.run(["python", "scripts/notification_router.py", "critical", "SOF incident requires manual intervention"], capture_output=True)
    return 1

if __name__ == "__main__":
    sys.exit(respond())
