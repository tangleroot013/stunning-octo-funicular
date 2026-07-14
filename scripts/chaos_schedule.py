#!/usr/bin/env python3
"""Schedule chaos tests during low-traffic windows with automatic rollback."""

import random
import subprocess
import time
from datetime import datetime
from pathlib import Path

CHAOS_WINDOW = (2, 5)  # 2 AM to 5 AM

def schedule() -> int:
    now = datetime.now()
    if not (CHAOS_WINDOW[0] <= now.hour < CHAOS_WINDOW[1]):
        print(f"ℹ️  Outside chaos window ({CHAOS_WINDOW[0]}:00-{CHAOS_WINDOW[1]}:00). Skipping.")
        return 0
    
    print(f"🎲 Chaos window active. Running scheduled chaos test...")
    
    # Create rollback point
    subprocess.run(["python", "scripts/rollback_tag.py"], capture_output=True)
    
    # Pick random chaos test
    tests = ["scripts/chaos_test.py", "scripts/server_stress.py"]
    test = random.choice(tests)
    
    print(f"   Selected: {test}")
    result = subprocess.run(["python", test], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ Chaos test failed. Initiating rollback...")
        # Get latest rollback tag
        tags = subprocess.check_output(["git", "tag", "-l", "rollback-*"], text=True).splitlines()
        if tags:
            latest = sorted(tags)[-1]
            subprocess.run(["git", "reset", "--hard", latest], check=True)
            print(f"   ✅ Rolled back to {latest}")
        subprocess.run(["python", "scripts/notification_router.py", "critical", "Chaos test failed, rolled back"], capture_output=True)
        return 1
    
    print(f"   ✅ Chaos test passed.")
    return 0

if __name__ == "__main__":
    sys.exit(schedule())
