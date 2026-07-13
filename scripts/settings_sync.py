#!/usr/bin/env python3
"""Deep audit: find keys in settings.json that are never referenced in source code."""

import json
import re
import sys
from pathlib import Path

def flatten_keys(obj, prefix=""):
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f"{prefix}.{k}" if prefix else k
            keys.add(full)
            keys.update(flatten_keys(v, full))
    return keys

def scan() -> int:
    data = json.loads(Path("settings.json").read_text())
    config_keys = flatten_keys(data)
    
    # Read all source
    source_text = ""
    for py in Path("src").rglob("*.py"):
        source_text += py.read_text() + "\n"
    for py in Path("scripts").rglob("*.py"):
        source_text += py.read_text() + "\n"
    
    stale = []
    for key in config_keys:
        # Check if any part of the key path appears in source
        parts = key.split(".")
        found = False
        for part in parts:
            if re.search(rf'\\b{re.escape(part)}\\b', source_text):
                found = True
                break
        if not found:
            stale.append(key)
    
    if stale:
        print(f"⚠️  {len(stale)} setting key(s) may be unused:")
        for k in sorted(stale)[:20]:
            print(f"   {k}")
        return 1
    print(f"✅ All {len(config_keys)} config keys appear referenced in source.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
