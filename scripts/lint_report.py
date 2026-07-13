#!/usr/bin/env python3
"""Run ruff, black --check, mypy and write a markdown report."""

import subprocess
from pathlib import Path

TOOLS = {
    "ruff": ["ruff", "check", "src"],
    "black": ["black", "--check", "src"],
    "mypy": ["mypy", "src"],
}

def run() -> None:
    lines = ["# Lint Report\n"]
    for name, cmd in TOOLS.items():
        result = subprocess.run(cmd, capture_output=True, text=True)
        ok = result.returncode == 0
        lines.append(f"## {name}: {'✅ PASS' if ok else '❌ FAIL'}\n")
        if not ok:
            lines.append(f"```\n{result.stdout or result.stderr}\n```\n")
    Path("lint_report.md").write_text("\n".join(lines))
    print("✅ lint_report.md generated.")

if __name__ == "__main__":
    run()
