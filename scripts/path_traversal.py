#!/usr/bin/env python3
"""Detect file operations using user-controlled paths without sanitization."""

import ast
import sys
from pathlib import Path

RISKY_FUNCS = {"open", "os.path.join", "os.makedirs", "shutil.copy", "shutil.move"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    func_name = "open"
                elif isinstance(node.func, ast.Attribute) and node.func.attr in ("join", "makedirs", "copy", "move"):
                    func_name = node.func.attr
                
                if func_name:
                    # Check if any arg looks user-controlled
                    for arg in node.args:
                        if isinstance(arg, ast.Name):
                            if any(x in arg.id.lower() for x in ("user", "input", "param", "request", "path", "file", "filename")):
                                print(f"🚨 {py}:{node.lineno} {func_name}() with user-controlled path: '{arg.id}'")
                                print(f"   Sanitize with: pathlib.Path(user_input).resolve() and check against base_dir")
                                hits += 1
    if hits:
        print(f"\n❌ {hits} potential path traversal vector(s).")
        return 1
    print("✅ File path operations look safe.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
