#!/usr/bin/env python3
"""Detect insecure random usage: random for crypto/secrets instead of secrets module."""

import ast
import sys
from pathlib import Path

DANGEROUS = {"random.random", "random.randint", "random.choice", "random.shuffle", "random.sample"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    full = ""
                    n = node.func
                    if isinstance(n.value, ast.Name) and n.value.id == "random":
                        full = f"random.{n.attr}"
                    if full in DANGEROUS:
                        print(f"🚨 {py}:{node.lineno} insecure random: {full}")
                        print(f"   Use: secrets.token_hex(), secrets.choice(), or os.urandom()")
                        hits += 1
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "random":
                        print(f"⚠️  {py}:{node.lineno} imports random — verify not used for security")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} insecure random usage(s). Use secrets module for cryptographic operations.")
        return 1
    print("✅ No insecure random usage detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
