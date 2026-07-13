#!/usr/bin/env python3
"""Check installed packages against known CVEs via pip-audit or safety."""

import subprocess
import sys
from pathlib import Path

def check() -> int:
    # Try pip-audit first
    result = subprocess.run([sys.executable, "-m", "pip_audit"], capture_output=True, text=True)
    if result.returncode == 0 or "No known vulnerabilities found" in result.stdout:
        print("✅ No known CVEs (pip-audit)")
        return 0
    
    # Fallback to safety
    result = subprocess.run([sys.executable, "-m", "safety", "check"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ No known CVEs (safety)")
        return 0
    
    print(f"⚠️  CVE scan results:\\n{result.stdout[-2000:]}")
    print("   Run: pip install pip-audit && python -m pip_audit")
    return 1

if __name__ == "__main__":
    sys.exit(check())
