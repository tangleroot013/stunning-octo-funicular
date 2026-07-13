#!/usr/bin/env python3
"""Generate ASCII art branch topology showing merge relationships."""

import subprocess
from pathlib import Path

def graph() -> None:
    log = subprocess.check_output(
        ["git", "log", "--all", "--graph", "--oneline", "--decorate", "--simplify-by-decoration"],
        text=True
    )
    print("# Branch Topology\n")
    print("```")
    print(log.strip())
    print("```")

if __name__ == "__main__":
    graph()
