#!/usr/bin/env python3
"""Aggregate all reports into a single markdown dashboard: OMNIBUS.md."""

import json
import subprocess
from pathlib import Path

REPORTS = {
    "Workspace Audit": "scripts/workspace_audit.py",
    "Lint Report": "scripts/lint_report.py",
    "TODO Scan": "scripts/todo_scan.py",
    "Size Report": "scripts/size_report.py",
    "Secret Scan": "scripts/secret_scan.py",
    "Dep Audit": "scripts/audit_deps.py",
}

def build() -> None:
    lines = ["# Omnibus Dashboard\\n", f"Generated: {__import__('datetime').datetime.now().isoformat()}\\n"]
    for title, script in REPORTS.items():
        lines.append(f"\\n## {title}\\n")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        output = (result.stdout or result.stderr or "No output").strip()
        lines.append("```\\n" + output[-2000:] + "\\n```")
        lines.append(f"\\n**Status:** {'✅ PASS' if result.returncode == 0 else '❌ FAIL'}")
    Path("OMNIBUS.md").write_text("\\n".join(lines))
    print("✅ OMNIBUS.md generated with all reports.")

if __name__ == "__main__":
    build()
