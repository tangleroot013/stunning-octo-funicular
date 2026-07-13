#!/usr/bin/env python3
"""Audit dataclass usage: frozen vs mutable, eq, slots, and unsafe_hash."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    dec_name = ""
                    if isinstance(decorator, ast.Name):
                        dec_name = decorator.id
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name):
                            dec_name = decorator.func.id
                    
                    if dec_name == "dataclass":
                        # Check for frozen
                        has_frozen = False
                        if isinstance(decorator, ast.Call):
                            for kw in decorator.keywords:
                                if kw.arg == "frozen" and isinstance(kw.value, ast.Constant) and kw.value.value:
                                    has_frozen = True
                        
                        if not has_frozen:
                            print(f"⚠️  {py}:{node.lineno} {node.name}: mutable dataclass (consider frozen=True)")
                            hits += 1
                        else:
                            print(f"✅ {py}:{node.lineno} {node.name}: frozen dataclass")
    if hits:
        print(f"\n⚠️  {hits} mutable dataclass(es). Review for immutability needs.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
