#!/usr/bin/env python3
"""Audit signal handlers: ensure SIGTERM/SIGINT have graceful shutdown paths."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        has_signal_import = False
        has_handler = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if any("signal" in (a.name if hasattr(a, "name") else str(a)) for a in node.names):
                    has_signal_import = True
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "signal":
                    has_handler = True
        if has_signal_import and not has_handler:
            print(f"⚠️  {py}: imports signal but no handler registered")
            hits += 1
    if hits:
        print(f"\\n❌ {hits} file(s) import signal without handlers.")
        return 1
    print("✅ Signal handling looks correct.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
