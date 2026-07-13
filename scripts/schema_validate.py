#!/usr/bin/env python3
"""Validate all .json files against settings.schema.json if it exists."""

import json
import sys
from pathlib import Path

def validate() -> int:
    schema_file = Path("settings.schema.json")
    if not schema_file.exists():
        print("ℹ️  No settings.schema.json found. Run: python scripts/settings_schema.py")
        return 0
    
    schema = json.loads(schema_file.read_text())
    fails = 0
    for j in Path(".").rglob("*.json"):
        if ".git" in str(j) or j.name == "settings.schema.json":
            continue
        try:
            data = json.loads(j.read_text())
            # Naive required-key check only
            required = schema.get("required", [])
            missing = set(required) - set(data.keys()) if isinstance(data, dict) else set()
            if missing:
                print(f"❌ {j}: missing required keys {missing}")
                fails += 1
            else:
                print(f"✅ {j}")
        except json.JSONDecodeError as exc:
            print(f"❌ {j}: invalid JSON ({exc})")
            fails += 1
    return fails

if __name__ == "__main__":
    sys.exit(validate())
