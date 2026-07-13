#!/usr/bin/env python3
"""Mutation-test lite: randomly corrupt one assertion per run to verify the suite actually catches failures."""

import ast
import random
import subprocess
import sys
from pathlib import Path

def mutate(target: Path) -> Path:
    tree = ast.parse(target.read_text())
    asserts = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if not asserts:
        return target
    victim = random.choice(asserts)
    # Wrap the test body in a try/except that flips the assert
    source = target.read_text().splitlines()
    line = victim.lineno - 1
    indent = len(source[line]) - len(source[line].lstrip())
    source[line] = " " * indent + "assert not (" + source[line].strip()[7:] + ")  # CHAOS: inverted"
    backup = target.with_suffix(".py.bak")
    backup.write_text(target.read_text())
    target.write_text("\n".join(source))
    return backup

def chaos() -> int:
    tests = list(Path("tests").rglob("test_*.py"))
    if not tests:
        print("ℹ️  No tests found.")
        return 0
    target = random.choice(tests)
    print(f"🎲 Mutating {target.name}...")
    backup = mutate(target)
    result = subprocess.run([sys.executable, "-m", "pytest", str(target), "-x", "-q"])
    target.write_text(backup.read_text())
    backup.unlink()
    if result.returncode == 0:
        print("🚨 CRITICAL: Test suite passed after mutation! Assertions may be tautological.")
        return 1
    print("✅ Mutation caught. Suite is healthy.")
    return 0

if __name__ == "__main__":
    sys.exit(chaos())
