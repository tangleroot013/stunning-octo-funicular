#!/usr/bin/env python3
"""Generate a new git hook template from settings.json pre-commit config."""

import json
from pathlib import Path

def generate() -> None:
    data = json.loads(Path("settings.json").read_text())
    hooks = data.get("ci", {}).get("pre_commit", {}).get("hooks", [])
    
    lines = ["#!/bin/sh", "# Auto-generated from settings.json", ""]
    for hook in hooks:
        if hook == "detect-secrets":
            lines.append('python scripts/secret_scan.py || exit 1')
        elif hook == "py_compile":
            lines.append('python -m py_compile hatch.py ship.py || exit 1')
        elif hook == "ruff":
            lines.append('ruff check src --fix || exit 1')
        elif hook == "black":
            lines.append('black --check src || exit 1')
        elif hook == "isort":
            lines.append('isort --check-only src || exit 1')
        elif hook == "trailing-whitespace":
            lines.append('git diff --cached --check || exit 1')
    
    out = Path(".git/hooks/pre-commit")
    out.write_text("\n".join(lines) + "\n")
    out.chmod(0o755)
    print(f"✅ Generated {out} with {len(hooks)} hook(s)")

if __name__ == "__main__":
    generate()
