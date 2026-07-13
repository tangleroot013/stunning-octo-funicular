#!/usr/bin/env python3
"""Validate all .json files in the repo are well-formed and sorted keys if applicable."""

import json
import sys
from pathlib import Path

def validate() -> int:
    fails = 0
    for j in Path(".").rglob("*.json"):
        if ".git" in str(j):
            continue
        try:
            data = json.loads(j.read_text())
            if j.name in ("settings.json", "pyproject.toml"):
                continue
            sorted_text = json.dumps(data, indent=2, sort_keys=True)
            if sorted_text != j.read_text():
                print(f"⚠️  {j} keys not sorted (run with --fix to rewrite)")
            else:
                print(f"✅ {j}")
        except json.JSONDecodeError as exc:
            print(f"❌ {j} invalid JSON: {exc}")
            fails += 1
    print(f"\\n{'✅ All JSON valid' if fails == 0 else f'❌ {fails} invalid file(s)'}")
    return fails

if __name__ == "__main__":
    sys.exit(validate())
