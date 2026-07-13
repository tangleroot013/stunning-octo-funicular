#!/usr/bin/env python3
"""Post-merge hook: auto-run dependency install and cache purge after git pull."""

import subprocess
from pathlib import Path

def post_merge() -> None:
    print("🔀 Merge detected. Running post-merge tasks...")
    
    # Check if requirements changed
    diff = subprocess.run(
        ["git", "diff", "HEAD@{1}", "--name-only"],
        capture_output=True, text=True
    ).stdout
    
    if "requirements" in diff:
        print("📦 requirements changed — reinstalling...")
        subprocess.run([subprocess.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Check if settings changed
    if "settings.json" in diff:
        print("⚙️  settings.json changed — syncing ignores...")
        subprocess.run([subprocess.sys.executable, "scripts/gitignore_sync.py"])
        subprocess.run([subprocess.sys.executable, "scripts/claudeignore_sync.py"])
    
    # Always purge caches
    subprocess.run([subprocess.sys.executable, "scripts/cache_purge.py"], capture_output=True)
    print("✅ Post-merge complete.")

if __name__ == "__main__":
    post_merge()
