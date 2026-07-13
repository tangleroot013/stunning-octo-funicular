#!/usr/bin/env python3
"""Chain all pre-commit hooks and emit an aggregate pass/fail report."""

import json
import subprocess
import sys
from pathlib import Path

def chain() -> int:
    data = json.loads(Path("settings.json").read_text())
    hooks = data.get("ci", {}).get("pre_commit", {}).get("hooks", [])
    results = []
    for hook in hooks:
        print(f"\\n{'─'*40}\\n🔷 {hook}")
        if hook == "detect-secrets":
            cmd = [sys.executable, "scripts/secret_scan.py"]
        elif hook == "py_compile":
            cmd = [sys.executable, "-m", "py_compile", "hatch.py", "ship.py"]
        elif hook == "ruff":
            cmd = ["ruff", "check", "src", "--fix"]
        elif hook == "black":
            cmd = ["black", "--check", "src"]
        elif hook == "isort":
            cmd = ["isort", "--check-only", "src"]
        elif hook == "trailing-whitespace":
            cmd = ["sed", "-i", "s/[[:space:]]*$//", "README.md"]
        else:
            continue
        result = subprocess.run(cmd, capture_output=True)
        ok = result.returncode == 0
        results.append((hook, ok))
        print(f"{'✅' if ok else '❌'} {hook}")
    
    passed = sum(1 for _, ok in results if ok)
    print(f"\\n{'='*40}\\nAggregate: {passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(chain())
