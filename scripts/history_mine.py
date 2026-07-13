#!/usr/bin/env python3
"""Mine shell history for commands containing the project directory name."""

import subprocess
import sys
from pathlib import Path

def mine() -> None:
    cwd = Path(".").resolve().name
    for hist_file in (Path.home() / ".zsh_history", Path.home() / ".bash_history"):
        if not hist_file.exists():
            continue
        text = hist_file.read_text(errors="ignore")
        matches = [line for line in text.splitlines() if cwd in line and "history" not in line]
        print(f"# {hist_file.name} ({len(matches)} matches for '{cwd}')\\n")
        for m in matches[-20:]:
            print(m.replace("\\n", ""))
        print()

if __name__ == "__main__":
    mine()
