#!/usr/bin/env python3
"""Verify all console_scripts entry points in pyproject.toml resolve to callable functions."""

import re
import sys
from pathlib import Path

def check() -> int:
    text = Path("pyproject.toml").read_text()
    scripts = re.findall(r'\\[project\\.scripts\\]\\n([^\\[]+)', text, re.DOTALL)
    if not scripts:
        print("ℹ️  No [project.scripts] section found.")
        return 0
    
    entries = re.findall(r'(\\w+)\\s*=\\s*"([^"]+)"', scripts[0])
    fails = 0
    for name, path in entries:
        mod, fn = path.rsplit(":", 1)
        try:
            import importlib
            module = importlib.import_module(mod)
            if not hasattr(module, fn):
                print(f"❌ {name} → {path}: function '{fn}' not found")
                fails += 1
            else:
                print(f"✅ {name} → {path}")
        except Exception as exc:
            print(f"❌ {name} → {path}: {exc}")
            fails += 1
    return fails

if __name__ == "__main__":
    sys.exit(check())
