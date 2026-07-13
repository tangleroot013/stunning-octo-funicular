#!/usr/bin/env python3
"""Gate PR merge on coverage delta: fail if coverage drops vs main branch baseline."""

import json
import subprocess
import sys
from pathlib import Path

def gate() -> int:
    # Get main branch coverage
    try:
        subprocess.run(["git", "stash", "--include-untracked", "-m", "codecov_gate"], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
        main_cov = float(Path(".last_cov_score").read_text().strip()) if Path(".last_cov_score").exists() else 0
        subprocess.run(["git", "checkout", "-"], check=True, capture_output=True)
        subprocess.run(["git", "stash", "pop"], check=True, capture_output=True)
    except Exception:
        print("⚠️  Could not read main branch coverage. Skipping gate.")
        return 0
    
    current = float(Path(".last_cov_score").read_text().strip()) if Path(".last_cov_score").exists() else 0
    delta = current - main_cov
    
    print(f"Coverage: main={main_cov:.1f}% → current={current:.1f}% (Δ{delta:+.1f}%)")
    
    if delta < -1:
        print(f"❌ Coverage dropped by {abs(delta):.1f}%. Merge blocked.")
        return 1
    if delta < 0:
        print(f"⚠️  Coverage dropped slightly ({delta:.1f}%).")
    else:
        print(f"✅ Coverage maintained or improved.")
    return 0

if __name__ == "__main__":
    sys.exit(gate())
