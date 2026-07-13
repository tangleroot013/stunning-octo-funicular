#!/usr/bin/env python3
"""Diff settings.json against the last committed version."""

import json
import subprocess
import sys
from pathlib import Path

def diff() -> int:
    try:
        old = subprocess.check_output(["git", "show", "HEAD:settings.json"], text=True)
    except subprocess.CalledProcessError:
        print("ℹ️  No committed settings.json to diff against.")
        return 0
    
    new = Path("settings.json").read_text()
    old_data = json.loads(old)
    new_data = json.loads(new)
    
    if old_data == new_data:
        print("✅ settings.json unchanged since last commit.")
        return 0
    
    # Simple key-level diff
    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())
    added = new_keys - old_keys
    removed = old_keys - new_keys
    changed = {k for k in (old_keys & new_keys) if old_data[k] != new_data[k]}
    
    if added:
        print(f"➕ Added sections: {added}")
    if removed:
        print(f"➖ Removed sections: {removed}")
    if changed:
        print(f"✏️  Modified sections: {changed}")
    return 1

if __name__ == "__main__":
    sys.exit(diff())
