#!/usr/bin/env python3
"""Map custom exception classes and detect bare except clauses."""

import ast
import sys
from pathlib import Path

def audit() -> None:
    exceptions = []
    bare_excepts = 0
    
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(isinstance(base, ast.Name) and base.id == "Exception" for base in node.bases):
                    exceptions.append(f"{py}:{node.lineno} {node.name}")
            
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    bare_excepts += 1
                    print(f"🚨 {py}:{node.lineno} bare except: (catches BaseException)")
    
    if exceptions:
        print(f"\n# Custom Exceptions ({len(exceptions)})")
        for e in exceptions:
            print(f"  {e}")
    else:
        print("ℹ️  No custom exceptions found.")
    
    if bare_excepts:
        print(f"\n❌ {bare_excepts} bare except clause(s). Use 'except Exception:' minimum.")
    else:
        print("\n✅ No bare except clauses.")

if __name__ == "__main__":
    audit()
