#!/usr/bin/env python3
"""Merge settings.local.json into settings.json with deep override."""

import json
from pathlib import Path

def merge() -> None:
    base = Path("settings.json")
    local = Path("settings.local.json")
    
    if not local.exists():
        print("ℹ️  No settings.local.json found.")
        return
    
    data = json.loads(base.read_text())
    override = json.loads(local.read_text())
    
    def deep_merge(d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = deep_merge(d[k], v)
            else:
                d[k] = v
        return d
    
    merged = deep_merge(data, override)
    base.write_text(json.dumps(merged, indent=2) + "\n")
    print(f"✅ Merged {len(override)} top-level key(s) from settings.local.json")
    print(f"   Run: git checkout settings.json  # to restore")

if __name__ == "__main__":
    merge()
