#!/usr/bin/env python3
"""Scaffold a new hatch.py subcommand stub."""

import sys
from pathlib import Path

STUB = '''\
def run_{name}(args: list[str]) -> int:
    """TODO: Implement {name} subcommand."""
    print("{name} executed with args:", args)
    return 0
'''

def scaffold(name: str) -> None:
    path = Path("src") / "commands" / f"{name}.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STUB.format(name=name))
    print(f"✅ Stub created at {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: wizard_stub.py <command_name>")
        sys.exit(1)
    scaffold(sys.argv[1])
