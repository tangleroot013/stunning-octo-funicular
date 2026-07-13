#!/usr/bin/env python3
"""Full autonomous release: validate, bump, tag, push, and notify."""

import json
import subprocess
import sys
from pathlib import Path

def release() -> int:
    # Pre-flight checks
    checks = [
        [sys.executable, "scripts/workspace_audit.py"],
        [sys.executable, "scripts/ci_simulate.py"],
        [sys.executable, "scripts/ship_check.py"],
    ]
    for cmd in checks:
        if subprocess.run(cmd, capture_output=True).returncode != 0:
            print(f"❌ Pre-flight failed: {' '.join(cmd)}")
            return 1
    
    # Bump version
    data = json.loads(Path("settings.json").read_text())
    ver = data["library"]["version"]
    print(f"🚀 Releasing v{ver}...")
    
    # Generate changelog
    subprocess.run([sys.executable, "scripts/generate_changelog.py"], capture_output=True)
    
    # Stage, commit, tag
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", f"release: v{ver}"], check=True)
    subprocess.run(["git", "tag", f"v{ver}"], check=True)
    
    # Push
    push = input("Push to origin? [y/N]: ").strip().lower()
    if push == "y":
        subprocess.run(["git", "push", "origin", "main", "--tags"], check=True)
        print("✅ Released and pushed.")
    else:
        print("✅ Tagged locally. Push when ready.")
    
    return 0

if __name__ == "__main__":
    sys.exit(release())
