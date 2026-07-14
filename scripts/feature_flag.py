#!/usr/bin/env python3
"""Feature flag validator: ensure all feature flags in code are declared in settings.json."""

import ast
import json
import re
import sys
from pathlib import Path

def audit() -> int:
    data = json.loads(Path("settings.json").read_text())
    declared = set(data.get("feature_flags", {}).keys())
    
    # Detect feature flags in code
    used = set()
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        for match in re.finditer(r'feature_enabled\(["\\']([^"\\']+)["\\']\)', text):
            used.add(match.group(1))
        for match in re.finditer(r'features\.get\(["\\']([^"\\']+)["\\']\)', text):
            used.add(match.group(1))
    
    print(f"# Feature Flag Audit\n")
    print(f"Declared: {len(declared)}")
    print(f"Used:     {len(used)}")
    
    undeclared = used - declared
    unused = declared - used
    
    if undeclared:
        print(f"\n❌ Undeclared flags: {undeclared}")
    if unused:
        print(f"⚠️  Unused flags: {unused}")
    
    if not undeclared and not unused:
        print(f"\n✅ All feature flags synchronized.")
        return 0
    return 1 if undeclared else 0

if __name__ == "__main__":
    sys.exit(audit())
